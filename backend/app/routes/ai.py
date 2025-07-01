# app/routes/ai.py - ALVIN AI Routes (Claude Integration)
import json
import time
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from app import db
from app.models import User, Project, Scene, StoryObject, TokenUsageLog
from app.services.claude_service import ClaudeService
from app.services.token_service import TokenService

ai_bp = Blueprint('ai', __name__)

# Validation schemas
class IdeaAnalysisSchema(Schema):
    idea_text = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 10)
    story_intent = fields.Str(missing='general')
    target_audience = fields.Str(missing=None)
    preferred_genre = fields.Str(missing=None)

class ProjectFromIdeaSchema(Schema):
    idea_text = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 10)
    analysis_id = fields.Str(missing=None)
    title = fields.Str(missing=None)

class SceneAnalysisSchema(Schema):
    critic_type = fields.Str(required=True, validate=lambda x: x in [
        'structure', 'character', 'dialogue', 'pacing', 'emotion', 'plot'
    ])
    focus_areas = fields.List(fields.Str(), missing=[])

class StoryGenerationSchema(Schema):
    narrative_options = fields.Dict(missing={})
    target_length = fields.Str(missing='medium', validate=lambda x: x in ['short', 'medium', 'long'])
    style_preferences = fields.Dict(missing={})

class TokenEstimateSchema(Schema):
    operation_type = fields.Str(required=True)
    input_text = fields.Str(required=True)
    target_length = fields.Str(missing='medium')

@ai_bp.route('/analyze-idea', methods=['POST'])
@jwt_required()
def analyze_idea():
    """Analyze a story idea using Claude AI"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': 'The authenticated user was not found'
        }), 404
    
    try:
        # Validate input
        schema = IdeaAnalysisSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Estimate token cost
    token_service = TokenService()
    estimated_cost = token_service.estimate_operation_cost(
        'analyze_idea', 
        data['idea_text']
    )
    
    # Check if user can afford the operation
    if not user.can_afford_tokens(estimated_cost):
        return jsonify({
            'error': 'Insufficient tokens',
            'message': f'This operation requires {estimated_cost} tokens. You have {user.get_remaining_tokens()} remaining.',
            'tokens_needed': estimated_cost,
            'tokens_available': user.get_remaining_tokens()
        }), 402
    
    try:
        start_time = time.time()
        
        # Use Claude service to analyze the idea
        claude_service = ClaudeService()
        analysis_result = claude_service.analyze_story_idea(
            idea_text=data['idea_text'],
            story_intent=data.get('story_intent'),
            target_audience=data.get('target_audience'),
            preferred_genre=data.get('preferred_genre')
        )
        
        response_time = int((time.time() - start_time) * 1000)
        
        # Log token usage
        token_log = TokenUsageLog(
            user_id=current_user_id,
            operation_type='analyze_idea',
            input_tokens=analysis_result.get('usage', {}).get('input_tokens', 0),
            output_tokens=analysis_result.get('usage', {}).get('output_tokens', 0),
            total_cost=estimated_cost,
            ai_model_used=claude_service.model,
            response_time_ms=response_time,
            operation_metadata={
                'story_intent': data.get('story_intent'),
                'idea_length': len(data['idea_text'])
            }
        )
        
        # Update user token usage
        user.tokens_used += estimated_cost
        
        db.session.add(token_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analysis': analysis_result['analysis'],
            'tokens_used': estimated_cost,
            'tokens_remaining': user.get_remaining_tokens()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Idea analysis error: {str(e)}")
        return jsonify({
            'error': 'Analysis failed',
            'message': 'An error occurred while analyzing your idea'
        }), 500

@ai_bp.route('/create-project-from-idea', methods=['POST'])
@jwt_required()
def create_project_from_idea():
    """Create a project from an analyzed story idea"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': 'The authenticated user was not found'
        }), 404
    
    try:
        # Validate input
        schema = ProjectFromIdeaSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Check project limits
    current_project_count = Project.query.filter_by(user_id=current_user_id).count()
    plan_limits = {'free': 3, 'pro': 50, 'enterprise': 1000}
    max_projects = plan_limits.get(user.plan, 3)
    
    if current_project_count >= max_projects:
        return jsonify({
            'error': 'Project limit reached',
            'message': f'Your {user.plan} plan allows up to {max_projects} projects'
        }), 403
    
    # Estimate token cost for project creation
    token_service = TokenService()
    estimated_cost = token_service.estimate_operation_cost(
        'create_project_from_idea', 
        data['idea_text']
    )
    
    # Check if user can afford the operation
    if not user.can_afford_tokens(estimated_cost):
        return jsonify({
            'error': 'Insufficient tokens',
            'message': f'This operation requires {estimated_cost} tokens. You have {user.get_remaining_tokens()} remaining.',
            'tokens_needed': estimated_cost,
            'tokens_available': user.get_remaining_tokens()
        }), 402
    
    try:
        start_time = time.time()
        
        # Use Claude service to create project structure
        claude_service = ClaudeService()
        project_data = claude_service.create_project_from_idea(
            idea_text=data['idea_text'],
            title_override=data.get('title')
        )
        
        response_time = int((time.time() - start_time) * 1000)
        
        # Create the project
        project = Project(
            title=project_data.get('title', 'Untitled Story'),
            description=project_data.get('description', ''),
            genre=project_data.get('genre'),
            original_idea=data['idea_text'],
            attributes=project_data.get('attributes', {}),
            tone=project_data.get('tone'),
            target_audience=project_data.get('target_audience'),
            estimated_scope=project_data.get('estimated_scope'),
            marketability=project_data.get('marketability'),
            target_word_count=project_data.get('target_word_count'),
            user_id=current_user_id
        )
        
        db.session.add(project)
        db.session.flush()  # Get project ID
        
        # Create initial scenes if provided
        if 'scenes' in project_data:
            for i, scene_data in enumerate(project_data['scenes']):
                scene = Scene(
                    title=scene_data.get('title', f'Scene {i+1}'),
                    description=scene_data.get('description', ''),
                    scene_type=scene_data.get('type', 'development'),
                    order_index=i + 1,
                    emotional_intensity=scene_data.get('emotional_intensity', 0.5),
                    project_id=project.id
                )
                db.session.add(scene)
        
        # Create story objects if provided
        if 'story_objects' in project_data:
            for obj_data in project_data['story_objects']:
                story_obj = StoryObject(
                    name=obj_data.get('name'),
                    object_type=obj_data.get('type', 'character'),
                    description=obj_data.get('description', ''),
                    importance=obj_data.get('importance', 'medium'),
                    character_role=obj_data.get('role') if obj_data.get('type') == 'character' else None,
                    project_id=project.id
                )
                db.session.add(story_obj)
        
        # Log token usage
        token_log = TokenUsageLog(
            user_id=current_user_id,
            operation_type='create_project_from_idea',
            input_tokens=project_data.get('usage', {}).get('input_tokens', 0),
            output_tokens=project_data.get('usage', {}).get('output_tokens', 0),
            total_cost=estimated_cost,
            project_id=project.id,
            ai_model_used=claude_service.model,
            response_time_ms=response_time,
            operation_metadata={
                'idea_length': len(data['idea_text']),
                'scenes_created': len(project_data.get('scenes', [])),
                'objects_created': len(project_data.get('story_objects', []))
            }
        )
        
        # Update user token usage
        user.tokens_used += estimated_cost
        
        db.session.add(token_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Project created successfully',
            'project': project.to_dict(include_scenes=True, include_objects=True),
            'tokens_used': estimated_cost,
            'tokens_remaining': user.get_remaining_tokens()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Project creation from idea error: {str(e)}")
        return jsonify({
            'error': 'Project creation failed',
            'message': 'An error occurred while creating the project'
        }), 500

@ai_bp.route('/projects/<project_id>/analyze-structure', methods=['POST'])
@jwt_required()
def analyze_project_structure(project_id):
    """Analyze the structure of a project"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Verify project access
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Get project scenes for analysis
    scenes = Scene.query.filter_by(project_id=project_id).order_by(Scene.order_index).all()
    if not scenes:
        return jsonify({
            'error': 'No scenes to analyze',
            'message': 'Please add some scenes to your project before analyzing structure'
        }), 400
    
    # Estimate token cost
    scenes_text = ' '.join([f"{scene.title}: {scene.description}" for scene in scenes])
    token_service = TokenService()
    estimated_cost = token_service.estimate_operation_cost('analyze_structure', scenes_text)
    
    # Check if user can afford the operation
    if not user.can_afford_tokens(estimated_cost):
        return jsonify({
            'error': 'Insufficient tokens',
            'message': f'This operation requires {estimated_cost} tokens. You have {user.get_remaining_tokens()} remaining.',
            'tokens_needed': estimated_cost,
            'tokens_available': user.get_remaining_tokens()
        }), 402
    
    try:
        start_time = time.time()
        
        # Use Claude service to analyze structure
        claude_service = ClaudeService()
        analysis_result = claude_service.analyze_story_structure(project, scenes)
        
        response_time = int((time.time() - start_time) * 1000)
        
        # Log token usage
        token_log = TokenUsageLog(
            user_id=current_user_id,
            operation_type='analyze_structure',
            input_tokens=analysis_result.get('usage', {}).get('input_tokens', 0),
            output_tokens=analysis_result.get('usage', {}).get('output_tokens', 0),
            total_cost=estimated_cost,
            project_id=project_id,
            ai_model_used=claude_service.model,
            response_time_ms=response_time,
            operation_metadata={
                'scenes_count': len(scenes),
                'project_phase': project.current_phase
            }
        )
        
        # Update user token usage
        user.tokens_used += estimated_cost
        
        db.session.add(token_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analysis': analysis_result['analysis'],
            'tokens_used': estimated_cost,
            'tokens_remaining': user.get_remaining_tokens()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Structure analysis error: {str(e)}")
        return jsonify({
            'error': 'Analysis failed',
            'message': 'An error occurred while analyzing the structure'
        }), 500

@ai_bp.route('/projects/<project_id>/suggest-scenes', methods=['POST'])
@jwt_required()
def suggest_scenes(project_id):
    """Generate scene suggestions for a project"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Verify project access
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Get existing scenes for context
    existing_scenes = Scene.query.filter_by(project_id=project_id).order_by(Scene.order_index).all()
    
    # Estimate token cost
    context_text = f"{project.title} {project.description} {project.original_idea or ''}"
    token_service = TokenService()
    estimated_cost = token_service.estimate_operation_cost('suggest_scenes', context_text)
    
    # Check if user can afford the operation
    if not user.can_afford_tokens(estimated_cost):
        return jsonify({
            'error': 'Insufficient tokens',
            'message': f'This operation requires {estimated_cost} tokens. You have {user.get_remaining_tokens()} remaining.',
            'tokens_needed': estimated_cost,
            'tokens_available': user.get_remaining_tokens()
        }), 402
    
    try:
        start_time = time.time()
        
        # Use Claude service to generate scene suggestions
        claude_service = ClaudeService()
        suggestions_result = claude_service.suggest_scenes(project, existing_scenes)
        
        response_time = int((time.time() - start_time) * 1000)
        
        # Log token usage
        token_log = TokenUsageLog(
            user_id=current_user_id,
            operation_type='suggest_scenes',
            input_tokens=suggestions_result.get('usage', {}).get('input_tokens', 0),
            output_tokens=suggestions_result.get('usage', {}).get('output_tokens', 0),
            total_cost=estimated_cost,
            project_id=project_id,
            ai_model_used=claude_service.model,
            response_time_ms=response_time,
            operation_metadata={
                'existing_scenes_count': len(existing_scenes),
                'suggestions_count': len(suggestions_result.get('suggestions', []))
            }
        )
        
        # Update user token usage
        user.tokens_used += estimated_cost
        
        db.session.add(token_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'suggestions': suggestions_result['suggestions'],
            'tokens_used': estimated_cost,
            'tokens_remaining': user.get_remaining_tokens()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Scene suggestion error: {str(e)}")
        return jsonify({
            'error': 'Suggestion failed',
            'message': 'An error occurred while generating scene suggestions'
        }), 500

@ai_bp.route('/projects/<project_id>/scenes/<int:scene_id>/analyze', methods=['POST'])
@jwt_required()
def analyze_scene(project_id, scene_id):
    """Analyze a specific scene"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Verify project access
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Get the scene
    scene = Scene.query.filter_by(id=scene_id, project_id=project_id).first()
    if not scene:
        return jsonify({
            'error': 'Scene not found',
            'message': 'The requested scene was not found'
        }), 404
    
    try:
        # Validate input
        schema = SceneAnalysisSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Estimate token cost
    scene_text = f"{scene.title} {scene.description} {scene.content or ''}"
    token_service = TokenService()
    estimated_cost = token_service.estimate_operation_cost('analyze_scene', scene_text)
    
    # Check if user can afford the operation
    if not user.can_afford_tokens(estimated_cost):
        return jsonify({
            'error': 'Insufficient tokens',
            'message': f'This operation requires {estimated_cost} tokens. You have {user.get_remaining_tokens()} remaining.',
            'tokens_needed': estimated_cost,
            'tokens_available': user.get_remaining_tokens()
        }), 402
    
    try:
        start_time = time.time()
        
        # Use Claude service to analyze the scene
        claude_service = ClaudeService()
        analysis_result = claude_service.analyze_scene(
            scene, 
            data['critic_type'], 
            data.get('focus_areas', [])
        )
        
        response_time = int((time.time() - start_time) * 1000)
        
        # Store analysis data in the scene
        if not scene.analysis_data:
            scene.analysis_data = {}
        scene.analysis_data[data['critic_type']] = analysis_result['analysis']
        scene.updated_at = datetime.utcnow()
        
        # Log token usage
        token_log = TokenUsageLog(
            user_id=current_user_id,
            operation_type='analyze_scene',
            input_tokens=analysis_result.get('usage', {}).get('input_tokens', 0),
            output_tokens=analysis_result.get('usage', {}).get('output_tokens', 0),
            total_cost=estimated_cost,
            project_id=project_id,
            scene_id=scene_id,
            ai_model_used=claude_service.model,
            response_time_ms=response_time,
            operation_metadata={
                'critic_type': data['critic_type'],
                'focus_areas': data.get('focus_areas', []),
                'scene_word_count': scene.word_count
            }
        )
        
        # Update user token usage
        user.tokens_used += estimated_cost
        
        db.session.add(token_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analysis': analysis_result['analysis'],
            'scene': scene.to_dict(),
            'tokens_used': estimated_cost,
            'tokens_remaining': user.get_remaining_tokens()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Scene analysis error: {str(e)}")
        return jsonify({
            'error': 'Analysis failed',
            'message': 'An error occurred while analyzing the scene'
        }), 500

@ai_bp.route('/projects/<project_id>/generate-story', methods=['POST'])
@jwt_required()
def generate_story(project_id):
    """Generate a full story from project scenes"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Verify project access
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Get project scenes
    scenes = Scene.query.filter_by(project_id=project_id).order_by(Scene.order_index).all()
    if not scenes:
        return jsonify({
            'error': 'No scenes to generate from',
            'message': 'Please add some scenes to your project before generating a story'
        }), 400
    
    try:
        # Validate input
        schema = StoryGenerationSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Estimate token cost (this is expensive)
    scenes_text = ' '.join([f"{scene.title}: {scene.description}" for scene in scenes])
    token_service = TokenService()
    estimated_cost = token_service.estimate_operation_cost(
        'generate_story', 
        scenes_text, 
        target_length=data.get('target_length', 'medium')
    )
    
    # Check if user can afford the operation
    if not user.can_afford_tokens(estimated_cost):
        return jsonify({
            'error': 'Insufficient tokens',
            'message': f'This operation requires {estimated_cost} tokens. You have {user.get_remaining_tokens()} remaining.',
            'tokens_needed': estimated_cost,
            'tokens_available': user.get_remaining_tokens()
        }), 402
    
    try:
        start_time = time.time()
        
        # Use Claude service to generate the full story
        claude_service = ClaudeService()
        story_result = claude_service.generate_full_story(
            project, 
            scenes, 
            data.get('narrative_options', {}),
            data.get('target_length', 'medium'),
            data.get('style_preferences', {})
        )
        
        response_time = int((time.time() - start_time) * 1000)
        
        # Update project with generated content
        project.current_phase = 'story'
        project.current_word_count = story_result.get('word_count', 0)
        project.updated_at = datetime.utcnow()
        
        # Log token usage
        token_log = TokenUsageLog(
            user_id=current_user_id,
            operation_type='generate_story',
            input_tokens=story_result.get('usage', {}).get('input_tokens', 0),
            output_tokens=story_result.get('usage', {}).get('output_tokens', 0),
            total_cost=estimated_cost,
            project_id=project_id,
            ai_model_used=claude_service.model,
            response_time_ms=response_time,
            operation_metadata={
                'scenes_count': len(scenes),
                'target_length': data.get('target_length', 'medium'),
                'generated_word_count': story_result.get('word_count', 0)
            }
        )
        
        # Update user token usage
        user.tokens_used += estimated_cost
        
        db.session.add(token_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'story': story_result['story'],
            'project': project.to_dict(),
            'tokens_used': estimated_cost,
            'tokens_remaining': user.get_remaining_tokens()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Story generation error: {str(e)}")
        return jsonify({
            'error': 'Generation failed',
            'message': 'An error occurred while generating the story'
        }), 500

@ai_bp.route('/token-estimate', methods=['POST'])
@jwt_required()
def estimate_tokens():
    """Estimate token cost for an operation"""
    try:
        # Validate input
        schema = TokenEstimateSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': 'The authenticated user was not found'
        }), 404
    
    try:
        # Calculate estimate
        token_service = TokenService()
        estimated_cost = token_service.estimate_operation_cost(
            data['operation_type'],
            data['input_text'],
            target_length=data.get('target_length', 'medium')
        )
        
        can_afford = user.can_afford_tokens(estimated_cost)
        
        return jsonify({
            'estimate': {
                'operation_type': data['operation_type'],
                'estimated_total_cost': estimated_cost,
                'input_length': len(data['input_text']),
                'target_length': data.get('target_length', 'medium')
            },
            'user_tokens': {
                'available': user.get_remaining_tokens(),
                'limit': user.tokens_limit,
                'used': user.tokens_used
            },
            'can_afford': can_afford,
            'shortfall': max(0, estimated_cost - user.get_remaining_tokens()) if not can_afford else 0
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Token estimation error: {str(e)}")
        return jsonify({
            'error': 'Estimation failed',
            'message': 'An error occurred while estimating token cost'
        }), 500

@ai_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_ai_tasks():
    """Get recent AI task history for the user"""
    current_user_id = get_jwt_identity()
    
    # Query parameters
    limit = min(request.args.get('limit', 10, type=int), 50)
    operation_type = request.args.get('operation_type', '').strip()
    
    # Base query
    query = TokenUsageLog.query.filter_by(user_id=current_user_id)
    
    # Filter by operation type if specified
    if operation_type:
        query = query.filter_by(operation_type=operation_type)
    
    # Get recent tasks
    tasks = query.order_by(TokenUsageLog.created_at.desc()).limit(limit).all()
    
    # Format task data
    tasks_data = []
    for task in tasks:
        task_data = task.to_dict()
        
        # Add project and scene titles if available
        if task.project_id:
            project = Project.query.get(task.project_id)
            task_data['project_title'] = project.title if project else 'Unknown Project'
        
        if task.scene_id:
            scene = Scene.query.get(task.scene_id)
            task_data['scene_title'] = scene.title if scene else 'Unknown Scene'
        
        # Add status based on completion
        task_data['status'] = 'completed' if task.billed_at else 'completed'
        
        tasks_data.append(task_data)
    
    return jsonify({
        'tasks': tasks_data,
        'total_count': query.count()
    }), 200