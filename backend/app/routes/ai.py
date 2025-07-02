# backend/app/routes/ai.py - ALVIN AI Routes (Simplified)
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
import json
import uuid

ai_bp = Blueprint('ai', __name__)

# Validation schemas
class AnalyzeIdeaSchema(Schema):
    idea = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 10)
    story_intent = fields.Str(missing='')
    target_audience = fields.Str(missing='general')
    preferred_genre = fields.Str(missing='')

class CreateProjectFromIdeaSchema(Schema):
    idea = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 10)
    title = fields.Str(missing='')
    analysis_id = fields.Str(missing='')

class AnalyzeSceneSchema(Schema):
    critic_type = fields.Str(required=True, validate=lambda x: x in [
        'structure', 'dialogue', 'pacing', 'character', 'setting', 'conflict'
    ])
    focus_areas = fields.List(fields.Str(), missing=[])

def verify_project_access(project_id, user_id):
    """Verify user has access to the project"""
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    return project

@ai_bp.route('/status', methods=['GET'])
def ai_status():
    """Get AI service status"""
    return jsonify({
        'ai_available': True,
        'simulation_mode': True,  # For development
        'version': '1.0.0',
        'message': 'AI service is operational (simulation mode)',
        'supported_operations': [
            'analyze-idea',
            'create-project-from-idea',
            'analyze-structure',
            'suggest-scenes',
            'generate-story',
            'analyze-scene'
        ]
    }), 200

@ai_bp.route('/analyze-idea', methods=['POST'])
@jwt_required()
def analyze_idea():
    """Analyze a story idea using AI"""
    current_user_id = get_jwt_identity()
    
    try:
        schema = AnalyzeIdeaSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Simulate AI analysis (replace with actual AI service)
    analysis_id = str(uuid.uuid4())
    
    # Mock analysis results
    analysis_result = {
        'analysis_id': analysis_id,
        'idea_text': data['idea'],
        'story_potential': 'High',
        'suggested_genre': detect_genre(data['idea']),
        'themes': extract_themes(data['idea']),
        'characters': suggest_characters(data['idea']),
        'settings': suggest_settings(data['idea']),
        'conflicts': suggest_conflicts(data['idea']),
        'feedback': generate_feedback(data['idea']),
        'suggestions': generate_suggestions(data['idea']),
        'estimated_word_count': estimate_word_count(data['idea']),
        'target_audience': data.get('target_audience', 'general'),
        'simulation_mode': True,
        'created_at': datetime.utcnow().isoformat()
    }
    
    return jsonify(analysis_result), 200

@ai_bp.route('/create-project-from-idea', methods=['POST'])
@jwt_required()
def create_project_from_idea():
    """Create a new project from analyzed idea"""
    current_user_id = get_jwt_identity()
    
    try:
        schema = CreateProjectFromIdeaSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Generate project details from idea
    title = data.get('title') or generate_title_from_idea(data['idea'])
    genre = detect_genre(data['idea'])
    
    # Create project
    project = Project(
        title=title,
        description=data['idea'][:500],  # Truncate if too long
        genre=genre,
        target_audience='general',
        current_phase='idea',
        user_id=current_user_id,
        created_from_ai=True
    )
    
    try:
        db.session.add(project)
        db.session.commit()
        
        # Generate initial scenes
        initial_scenes = generate_initial_scenes(data['idea'], project.id)
        
        return jsonify({
            'success': True,
            'message': 'Project created successfully from idea',
            'project': project.to_dict(),
            'suggested_scenes': initial_scenes,
            'next_steps': [
                'Review and edit the generated project details',
                'Develop the suggested scenes',
                'Add characters and story objects',
                'Begin writing your first scene'
            ]
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Project creation error: {str(e)}")
        return jsonify({
            'error': 'Project creation failed',
            'message': 'An error occurred while creating the project'
        }), 500

@ai_bp.route('/projects/<project_id>/analyze-structure', methods=['POST'])
@jwt_required()
def analyze_project_structure(project_id):
    """Analyze project structure using AI"""
    current_user_id = get_jwt_identity()
    
    # Verify project access
    project = verify_project_access(project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Get project data for analysis
    scenes = Scene.query.filter_by(project_id=project_id).order_by(Scene.order_index).all()
    objects = StoryObject.query.filter_by(project_id=project_id).all()
    
    # Simulate structure analysis
    analysis = {
        'project_id': project_id,
        'overall_assessment': analyze_story_structure(project, scenes),
        'scene_count': len(scenes),
        'character_count': len([obj for obj in objects if obj.object_type == 'character']),
        'plot_analysis': {
            'has_clear_beginning': len(scenes) > 0,
            'has_middle_development': len(scenes) > 2,
            'has_satisfying_end': any(scene.scene_type == 'resolution' for scene in scenes),
            'pacing_score': calculate_pacing_score(scenes)
        },
        'strengths': identify_strengths(project, scenes, objects),
        'weaknesses': identify_weaknesses(project, scenes, objects),
        'recommendations': generate_recommendations(project, scenes, objects),
        'next_phase_suggestion': suggest_next_phase(project),
        'simulation_mode': True,
        'analyzed_at': datetime.utcnow().isoformat()
    }
    
    return jsonify(analysis), 200

@ai_bp.route('/projects/<project_id>/suggest-scenes', methods=['POST'])
@jwt_required()
def suggest_scenes(project_id):
    """Generate scene suggestions for a project"""
    current_user_id = get_jwt_identity()
    
    # Verify project access
    project = verify_project_access(project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Get existing scenes to avoid duplication
    existing_scenes = Scene.query.filter_by(project_id=project_id).all()
    
    # Generate scene suggestions
    suggested_scenes = generate_scene_suggestions(project, existing_scenes)
    
    return jsonify({
        'project_id': project_id,
        'suggested_scenes': suggested_scenes,
        'total_suggestions': len(suggested_scenes),
        'simulation_mode': True,
        'generated_at': datetime.utcnow().isoformat()
    }), 200

@ai_bp.route('/projects/<project_id>/generate-story', methods=['POST'])
@jwt_required()
def generate_story(project_id):
    """Generate a complete story for the project"""
    current_user_id = get_jwt_identity()
    
    # Verify project access
    project = verify_project_access(project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Generate story content (simulation)
    story_content = generate_story_content(project)
    
    return jsonify({
        'project_id': project_id,
        'story_content': story_content,
        'word_count': len(story_content.split()),
        'estimated_reading_time': len(story_content.split()) // 200,  # ~200 WPM
        'simulation_mode': True,
        'generated_at': datetime.utcnow().isoformat()
    }), 200

@ai_bp.route('/projects/<project_id>/scenes/<scene_id>/analyze', methods=['POST'])
@jwt_required()
def analyze_scene(project_id, scene_id):
    """Analyze a specific scene"""
    current_user_id = get_jwt_identity()
    
    try:
        schema = AnalyzeSceneSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Verify project access
    project = verify_project_access(project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Get scene
    scene = Scene.query.filter_by(id=scene_id, project_id=project_id).first()
    if not scene:
        return jsonify({
            'error': 'Scene not found',
            'message': 'The requested scene was not found'
        }), 404
    
    # Analyze scene based on critic type
    analysis = analyze_scene_content(scene, data['critic_type'])
    
    return jsonify(analysis), 200

@ai_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_ai_tasks():
    """Get recent AI tasks for the user"""
    current_user_id = get_jwt_identity()
    limit = request.args.get('limit', 10, type=int)
    
    # Mock AI task history (replace with actual task tracking)
    tasks = generate_mock_tasks(current_user_id, limit)
    
    return jsonify({
        'tasks': tasks,
        'total': len(tasks),
        'simulation_mode': True
    }), 200

# Helper functions for AI simulation
def detect_genre(idea_text):
    """Detect genre from idea text (simulation)"""
    keywords = {
        'fantasy': ['magic', 'wizard', 'dragon', 'spell', 'quest', 'realm'],
        'sci-fi': ['space', 'robot', 'future', 'technology', 'alien', 'time'],
        'mystery': ['detective', 'murder', 'clue', 'investigation', 'suspect'],
        'romance': ['love', 'heart', 'relationship', 'wedding', 'kiss'],
        'thriller': ['chase', 'danger', 'escape', 'survival', 'threat'],
        'horror': ['ghost', 'haunted', 'nightmare', 'terror', 'dark']
    }
    
    idea_lower = idea_text.lower()
    scores = {}
    
    for genre, words in keywords.items():
        scores[genre] = sum(1 for word in words if word in idea_lower)
    
    return max(scores, key=scores.get) if max(scores.values()) > 0 else 'general'

def extract_themes(idea_text):
    """Extract potential themes (simulation)"""
    return ['Identity', 'Courage', 'Friendship', 'Good vs Evil', 'Coming of Age']

def suggest_characters(idea_text):
    """Suggest characters based on idea (simulation)"""
    return [
        {'name': 'Protagonist', 'role': 'main character', 'archetype': 'hero'},
        {'name': 'Mentor', 'role': 'guide', 'archetype': 'wise advisor'},
        {'name': 'Antagonist', 'role': 'opposition', 'archetype': 'villain'}
    ]

def suggest_settings(idea_text):
    """Suggest settings (simulation)"""
    return ['Primary Location', 'Secondary Location', 'Climax Setting']

def suggest_conflicts(idea_text):
    """Suggest conflicts (simulation)"""
    return ['Internal Conflict', 'External Conflict', 'Societal Conflict']

def generate_feedback(idea_text):
    """Generate AI feedback (simulation)"""
    return f"This is an intriguing concept with strong potential for development. The core idea shows promise for engaging storytelling."

def generate_suggestions(idea_text):
    """Generate improvement suggestions (simulation)"""
    return [
        "Consider developing the main character's motivation more deeply",
        "Add specific details about the setting to enhance world-building",
        "Introduce a compelling conflict early in the story"
    ]

def estimate_word_count(idea_text):
    """Estimate final word count (simulation)"""
    return len(idea_text.split()) * 50  # Rough estimation

def generate_title_from_idea(idea_text):
    """Generate a title from idea (simulation)"""
    words = idea_text.split()
    if len(words) >= 3:
        return f"The {words[1].title()} {words[2].title()}"
    return "Untitled Story"

def generate_initial_scenes(idea_text, project_id):
    """Generate initial scene suggestions (simulation)"""
    return [
        {
            'title': 'Opening Scene',
            'description': 'Introduce the main character and setting',
            'scene_type': 'opening',
            'estimated_words': 500
        },
        {
            'title': 'Inciting Incident',
            'description': 'The event that sets the story in motion',
            'scene_type': 'development',
            'estimated_words': 750
        },
        {
            'title': 'First Challenge',
            'description': 'The protagonist faces their first obstacle',
            'scene_type': 'development',
            'estimated_words': 600
        }
    ]

def analyze_story_structure(project, scenes):
    """Analyze overall story structure (simulation)"""
    if len(scenes) == 0:
        return "Project is in early development stage"
    elif len(scenes) < 3:
        return "Story structure needs more development"
    else:
        return "Story structure is developing well"

def calculate_pacing_score(scenes):
    """Calculate pacing score (simulation)"""
    if not scenes:
        return 0.0
    
    # Simple pacing calculation based on scene types
    action_scenes = sum(1 for scene in scenes if scene.scene_type in ['action', 'climax'])
    total_scenes = len(scenes)
    
    return min(action_scenes / total_scenes * 2, 1.0) if total_scenes > 0 else 0.0

def identify_strengths(project, scenes, objects):
    """Identify story strengths (simulation)"""
    strengths = []
    
    if len(scenes) > 5:
        strengths.append("Good scene development")
    if len(objects) > 3:
        strengths.append("Rich character and object development")
    if project.description and len(project.description) > 100:
        strengths.append("Clear project vision")
    
    return strengths or ["Strong foundation for development"]

def identify_weaknesses(project, scenes, objects):
    """Identify areas for improvement (simulation)"""
    weaknesses = []
    
    if len(scenes) < 3:
        weaknesses.append("Needs more scene development")
    if len([obj for obj in objects if obj.object_type == 'character']) < 2:
        weaknesses.append("Consider adding more characters")
    
    return weaknesses or ["Overall structure is solid"]

def generate_recommendations(project, scenes, objects):
    """Generate improvement recommendations (simulation)"""
    return [
        "Focus on developing character motivations",
        "Add more conflict to drive the story forward",
        "Consider the story's pacing and rhythm"
    ]

def suggest_next_phase(project):
    """Suggest next development phase (simulation)"""
    if project.current_phase == 'idea':
        return 'expansion'
    elif project.current_phase == 'expansion':
        return 'story'
    else:
        return 'refinement'

def generate_scene_suggestions(project, existing_scenes):
    """Generate scene suggestions (simulation)"""
    existing_count = len(existing_scenes)
    
    suggestions = [
        {
            'title': f'Scene {existing_count + 1}: Development',
            'description': 'Advance the plot with character interaction',
            'scene_type': 'development',
            'estimated_words': 600,
            'priority': 'high'
        },
        {
            'title': f'Scene {existing_count + 2}: Conflict',
            'description': 'Introduce a new challenge or obstacle',
            'scene_type': 'conflict',
            'estimated_words': 750,
            'priority': 'medium'
        }
    ]
    
    return suggestions

def generate_story_content(project):
    """Generate story content (simulation)"""
    return f"""
    {project.title}

    {project.description}

    This is a generated story beginning based on your project. The story would continue to develop the themes and characters you've outlined, building toward a compelling climax and resolution.

    [This is simulation content - replace with actual AI-generated story]
    """

def analyze_scene_content(scene, critic_type):
    """Analyze scene content by critic type (simulation)"""
    analysis_map = {
        'structure': {
            'score': 0.8,
            'feedback': 'Scene has good structure with clear beginning and development',
            'suggestions': ['Consider adding more tension', 'Strengthen the scene ending']
        },
        'dialogue': {
            'score': 0.7,
            'feedback': 'Dialogue feels natural but could be more distinctive',
            'suggestions': ['Give each character a unique voice', 'Add subtext to conversations']
        },
        'pacing': {
            'score': 0.75,
            'feedback': 'Pacing is generally good with room for improvement',
            'suggestions': ['Vary sentence length for rhythm', 'Consider cutting unnecessary details']
        }
    }
    
    result = analysis_map.get(critic_type, analysis_map['structure'])
    result.update({
        'scene_id': scene.id,
        'critic_type': critic_type,
        'word_count': scene.word_count or 0,
        'analyzed_at': datetime.utcnow().isoformat(),
        'simulation_mode': True
    })
    
    return result

def generate_mock_tasks(user_id, limit):
    """Generate mock AI task history (simulation)"""
    tasks = []
    task_types = ['analyze-idea', 'create-project', 'suggest-scenes', 'analyze-structure']
    
    for i in range(min(limit, 5)):
        tasks.append({
            'id': f'task_{user_id}_{i}',
            'type': task_types[i % len(task_types)],
            'status': 'completed',
            'created_at': (datetime.utcnow() - timedelta(hours=i)).isoformat(),
            'completed_at': (datetime.utcnow() - timedelta(hours=i) + timedelta(minutes=2)).isoformat(),
            'result_summary': f'Successfully completed {task_types[i % len(task_types)]} operation'
        })
    
    return tasks