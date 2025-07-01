# app/routes/projects.py - ALVIN Projects Routes
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from sqlalchemy import desc, asc, or_
from app import db
from app.models import User, Project, Scene, StoryObject
from app.services.export_service import ExportService
import io

projects_bp = Blueprint('projects', __name__)

# Validation schemas
class ProjectCreateSchema(Schema):
    title = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 1 and len(x) <= 200)
    description = fields.Str(missing='')
    genre = fields.Str(missing=None)
    target_word_count = fields.Int(missing=None, validate=lambda x: x is None or x > 0)
    original_idea = fields.Str(missing='')

class ProjectUpdateSchema(Schema):
    title = fields.Str(validate=lambda x: len(x.strip()) >= 1 and len(x) <= 200)
    description = fields.Str()
    genre = fields.Str(allow_none=True)
    current_phase = fields.Str(validate=lambda x: x in ['idea', 'expand', 'story'])
    target_word_count = fields.Int(allow_none=True, validate=lambda x: x is None or x > 0)
    current_word_count = fields.Int(validate=lambda x: x >= 0)
    status = fields.Str(validate=lambda x: x in ['active', 'paused', 'completed', 'archived'])
    tone = fields.Str(allow_none=True)
    target_audience = fields.Str(allow_none=True)
    estimated_scope = fields.Str(allow_none=True)
    marketability = fields.Int(allow_none=True, validate=lambda x: x is None or 1 <= x <= 5)

@projects_bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    """Get user's projects with filtering and pagination"""
    current_user_id = get_jwt_identity()
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('limit', current_app.config['PROJECTS_PER_PAGE']), 100)
    sort_by = request.args.get('sort', 'updated_at')
    sort_order = request.args.get('order', 'desc')
    search = request.args.get('search', '').strip()
    genre = request.args.get('genre', '').strip()
    status = request.args.get('status', '').strip()
    phase = request.args.get('phase', '').strip()
    
    # Base query
    query = Project.query.filter_by(user_id=current_user_id)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Project.title.ilike(f'%{search}%'),
                Project.description.ilike(f'%{search}%'),
                Project.original_idea.ilike(f'%{search}%')
            )
        )
    
    if genre:
        query = query.filter_by(genre=genre)
    
    if status:
        query = query.filter_by(status=status)
    
    if phase:
        query = query.filter_by(current_phase=phase)
    
    # Apply sorting
    sort_column = getattr(Project, sort_by, Project.updated_at)
    if sort_order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Paginate
    pagination = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'projects': [project.to_dict() for project in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    """Create a new project"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': 'The authenticated user was not found'
        }), 404
    
    try:
        # Validate input
        schema = ProjectCreateSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Check project limits for user's plan
    current_project_count = Project.query.filter_by(user_id=current_user_id).count()
    plan_limits = {
        'free': 3,
        'pro': 50,
        'enterprise': 1000
    }
    
    max_projects = plan_limits.get(user.plan, 3)
    if current_project_count >= max_projects:
        return jsonify({
            'error': 'Project limit reached',
            'message': f'Your {user.plan} plan allows up to {max_projects} projects'
        }), 403
    
    # Create project
    project = Project(
        title=data['title'].strip(),
        description=data.get('description', ''),
        genre=data.get('genre'),
        target_word_count=data.get('target_word_count'),
        original_idea=data.get('original_idea', ''),
        user_id=current_user_id
    )
    
    try:
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Project created successfully',
            'project': project.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Project creation error: {str(e)}")
        return jsonify({
            'error': 'Project creation failed',
            'message': 'An error occurred while creating the project'
        }), 500

@projects_bp.route('/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Get a specific project with full details"""
    current_user_id = get_jwt_identity()
    
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Include scenes and objects
    include_scenes = request.args.get('include_scenes', 'false').lower() == 'true'
    include_objects = request.args.get('include_objects', 'false').lower() == 'true'
    
    return jsonify({
        'project': project.to_dict(
            include_scenes=include_scenes,
            include_objects=include_objects
        )
    }), 200

@projects_bp.route('/<project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """Update a project"""
    current_user_id = get_jwt_identity()
    
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    try:
        # Validate input
        schema = ProjectUpdateSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Update project fields
    update_fields = [
        'title', 'description', 'genre', 'current_phase', 
        'target_word_count', 'current_word_count', 'status',
        'tone', 'target_audience', 'estimated_scope', 'marketability'
    ]
    
    for field in update_fields:
        if field in data:
            if field == 'title' and data[field]:
                setattr(project, field, data[field].strip())
            else:
                setattr(project, field, data[field])
    
    project.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Project updated successfully',
            'project': project.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Project update error: {str(e)}")
        return jsonify({
            'error': 'Project update failed',
            'message': 'An error occurred while updating the project'
        }), 500

@projects_bp.route('/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """Delete a project"""
    current_user_id = get_jwt_identity()
    
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    try:
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Project deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Project deletion error: {str(e)}")
        return jsonify({
            'error': 'Project deletion failed',
            'message': 'An error occurred while deleting the project'
        }), 500

@projects_bp.route('/<project_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_project(project_id):
    """Duplicate a project"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Get original project
    original_project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not original_project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Check project limits
    current_project_count = Project.query.filter_by(user_id=current_user_id).count()
    plan_limits = {'free': 3, 'pro': 50, 'enterprise': 1000}
    max_projects = plan_limits.get(user.plan, 3)
    
    if current_project_count >= max_projects:
        return jsonify({
            'error': 'Project limit reached',
            'message': f'Your {user.plan} plan allows up to {max_projects} projects'
        }), 403
    
    try:
        # Create duplicate project
        new_project = Project(
            title=f"{original_project.title} (Copy)",
            description=original_project.description,
            genre=original_project.genre,
            target_word_count=original_project.target_word_count,
            original_idea=original_project.original_idea,
            tone=original_project.tone,
            target_audience=original_project.target_audience,
            estimated_scope=original_project.estimated_scope,
            attributes=original_project.attributes,
            user_id=current_user_id
        )
        
        db.session.add(new_project)
        db.session.flush()  # Get the new project ID
        
        # Duplicate scenes
        original_scenes = Scene.query.filter_by(project_id=project_id).order_by(Scene.order_index).all()
        for scene in original_scenes:
            new_scene = Scene(
                title=scene.title,
                description=scene.description,
                content=scene.content,
                scene_type=scene.scene_type,
                order_index=scene.order_index,
                emotional_intensity=scene.emotional_intensity,
                project_id=new_project.id
            )
            db.session.add(new_scene)
        
        # Duplicate story objects
        original_objects = StoryObject.query.filter_by(project_id=project_id).all()
        for obj in original_objects:
            new_object = StoryObject(
                name=obj.name,
                object_type=obj.object_type,
                description=obj.description,
                importance=obj.importance,
                attributes=obj.attributes,
                symbolic_meaning=obj.symbolic_meaning,
                character_role=obj.character_role,
                project_id=new_project.id
            )
            db.session.add(new_object)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Project duplicated successfully',
            'project': new_project.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Project duplication error: {str(e)}")
        return jsonify({
            'error': 'Project duplication failed',
            'message': 'An error occurred while duplicating the project'
        }), 500

@projects_bp.route('/<project_id>/scenes', methods=['GET'])
@jwt_required()
def get_project_scenes(project_id):
    """Get all scenes for a project"""
    current_user_id = get_jwt_identity()
    
    # Verify project ownership
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    scenes = Scene.query.filter_by(project_id=project_id).order_by(Scene.order_index).all()
    
    return jsonify({
        'scenes': [scene.to_dict() for scene in scenes]
    }), 200

@projects_bp.route('/<project_id>/objects', methods=['GET'])
@jwt_required()
def get_project_objects(project_id):
    """Get all story objects for a project"""
    current_user_id = get_jwt_identity()
    
    # Verify project ownership
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Filter by object type if specified
    object_type = request.args.get('type')
    query = StoryObject.query.filter_by(project_id=project_id)
    
    if object_type:
        query = query.filter_by(object_type=object_type)
    
    objects = query.all()
    
    return jsonify({
        'objects': [obj.to_dict() for obj in objects]
    }), 200

@projects_bp.route('/<project_id>/stats', methods=['GET'])
@jwt_required()
def get_project_stats(project_id):
    """Get project statistics"""
    current_user_id = get_jwt_identity()
    
    # Verify project ownership
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Calculate statistics
    scenes_count = Scene.query.filter_by(project_id=project_id).count()
    objects_count = StoryObject.query.filter_by(project_id=project_id).count()
    characters_count = StoryObject.query.filter_by(project_id=project_id, object_type='character').count()
    locations_count = StoryObject.query.filter_by(project_id=project_id, object_type='location').count()
    
    # Word count statistics
    total_scene_words = db.session.query(db.func.sum(Scene.word_count)).filter_by(project_id=project_id).scalar() or 0
    
    # Progress calculation
    progress = project.get_progress_percentage()
    
    return jsonify({
        'stats': {
            'scenes_count': scenes_count,
            'objects_count': objects_count,
            'characters_count': characters_count,
            'locations_count': locations_count,
            'total_scene_words': total_scene_words,
            'current_word_count': project.current_word_count or 0,
            'target_word_count': project.target_word_count,
            'progress_percentage': progress,
            'completion_ratio': (project.current_word_count or 0) / project.target_word_count if project.target_word_count else 0
        }
    }), 200

@projects_bp.route('/<project_id>/export-story', methods=['GET'])
@jwt_required()
def export_project_story(project_id):
    """Export project story in various formats"""
    current_user_id = get_jwt_identity()
    
    # Verify project ownership
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Get export format
    export_format = request.args.get('format', 'txt').lower()
    if export_format not in ['txt', 'pdf', 'docx', 'epub']:
        return jsonify({
            'error': 'Invalid format',
            'message': 'Supported formats: txt, pdf, docx, epub'
        }), 400
    
    try:
        # Get all scenes for the project
        scenes = Scene.query.filter_by(project_id=project_id).order_by(Scene.order_index).all()
        
        # Use export service to generate file
        export_service = ExportService()
        file_data, filename, mimetype = export_service.export_story(
            project, scenes, export_format
        )
        
        return send_file(
            io.BytesIO(file_data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        current_app.logger.error(f"Story export error: {str(e)}")
        return jsonify({
            'error': 'Export failed',
            'message': 'An error occurred while exporting the story'
        }), 500