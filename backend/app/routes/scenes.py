# app/routes/scenes.py - ALVIN Scenes Routes
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from sqlalchemy import desc, asc
from app import db
from app.models import User, Project, Scene, SceneObject, StoryObject
import re

scenes_bp = Blueprint('scenes', __name__)

# Validation schemas
class SceneCreateSchema(Schema):
    title = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 1 and len(x) <= 200)
    description = fields.Str(missing='')
    content = fields.Str(missing='')
    scene_type = fields.Str(missing='development', validate=lambda x: x in [
        'opening', 'inciting', 'development', 'climax', 'resolution', 'transition'
    ])
    emotional_intensity = fields.Float(missing=0.5, validate=lambda x: 0.0 <= x <= 1.0)
    order_index = fields.Int(missing=None)
    project_id = fields.Str(required=True)

class SceneUpdateSchema(Schema):
    title = fields.Str(validate=lambda x: len(x.strip()) >= 1 and len(x) <= 200)
    description = fields.Str()
    content = fields.Str()
    scene_type = fields.Str(validate=lambda x: x in [
        'opening', 'inciting', 'development', 'climax', 'resolution', 'transition'
    ])
    emotional_intensity = fields.Float(validate=lambda x: 0.0 <= x <= 1.0)
    order_index = fields.Int()
    status = fields.Str(validate=lambda x: x in ['draft', 'completed', 'needs_review'])

class SceneReorderSchema(Schema):
    scene_order = fields.List(fields.Raw(), required=True)

def calculate_word_count(text):
    """Calculate word count from text content"""
    if not text:
        return 0
    # Remove HTML tags and count words
    clean_text = re.sub(r'<[^>]+>', '', text)
    words = re.findall(r'\b\w+\b', clean_text)
    return len(words)

def verify_project_access(project_id, user_id):
    """Verify user has access to the project"""
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    return project

@scenes_bp.route('', methods=['GET'])
@jwt_required()
def get_scenes():
    """Get scenes with filtering and pagination"""
    current_user_id = get_jwt_identity()
    
    # Get project ID from query params
    project_id = request.args.get('project_id')
    if not project_id:
        return jsonify({
            'error': 'Project ID required',
            'message': 'Please specify a project_id parameter'
        }), 400
    
    # Verify project access
    project = verify_project_access(project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('limit', current_app.config['SCENES_PER_PAGE']), 100)
    sort_by = request.args.get('sort', 'order_index')
    sort_order = request.args.get('order', 'asc')
    scene_type = request.args.get('type', '').strip()
    status = request.args.get('status', '').strip()
    
    # Base query
    query = Scene.query.filter_by(project_id=project_id)
    
    # Apply filters
    if scene_type:
        query = query.filter_by(scene_type=scene_type)
    
    if status:
        query = query.filter_by(status=status)
    
    # Apply sorting
    sort_column = getattr(Scene, sort_by, Scene.order_index)
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
        'scenes': [scene.to_dict() for scene in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

@scenes_bp.route('', methods=['POST'])
@jwt_required()
def create_scene():
    """Create a new scene"""
    current_user_id = get_jwt_identity()
    
    try:
        # Validate input
        schema = SceneCreateSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Verify project access
    project = verify_project_access(data['project_id'], current_user_id)
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Determine order index if not provided
    if data.get('order_index') is None:
        max_order = db.session.query(db.func.max(Scene.order_index)).filter_by(
            project_id=data['project_id']
        ).scalar()
        data['order_index'] = (max_order or 0) + 1
    
    # Calculate word count
    word_count = calculate_word_count(data.get('content', ''))
    
    # Create scene
    scene = Scene(
        title=data['title'].strip(),
        description=data.get('description', ''),
        content=data.get('content', ''),
        scene_type=data.get('scene_type', 'development'),
        order_index=data['order_index'],
        emotional_intensity=data.get('emotional_intensity', 0.5),
        word_count=word_count,
        project_id=data['project_id']
    )
    
    try:
        db.session.add(scene)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Scene created successfully',
            'scene': scene.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Scene creation error: {str(e)}")
        return jsonify({
            'error': 'Scene creation failed',
            'message': 'An error occurred while creating the scene'
        }), 500

@scenes_bp.route('/<int:scene_id>', methods=['GET'])
@jwt_required()
def get_scene(scene_id):
    """Get a specific scene"""
    current_user_id = get_jwt_identity()
    
    scene = Scene.query.get(scene_id)
    if not scene:
        return jsonify({
            'error': 'Scene not found',
            'message': 'The requested scene was not found'
        }), 404
    
    # Verify project access
    project = verify_project_access(scene.project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have access to this scene'
        }), 403
    
    # Include objects if requested
    include_objects = request.args.get('include_objects', 'false').lower() == 'true'
    
    return jsonify({
        'scene': scene.to_dict(include_objects=include_objects)
    }), 200

@scenes_bp.route('/<int:scene_id>', methods=['PUT'])
@jwt_required()
def update_scene(scene_id):
    """Update a scene"""
    current_user_id = get_jwt_identity()
    
    scene = Scene.query.get(scene_id)
    if not scene:
        return jsonify({
            'error': 'Scene not found',
            'message': 'The requested scene was not found'
        }), 404
    
    # Verify project access
    project = verify_project_access(scene.project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have access to this scene'
        }), 403
    
    try:
        # Validate input
        schema = SceneUpdateSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Update scene fields
    update_fields = [
        'title', 'description', 'content', 'scene_type', 
        'emotional_intensity', 'order_index', 'status'
    ]
    
    for field in update_fields:
        if field in data:
            if field == 'title' and data[field]:
                setattr(scene, field, data[field].strip())
            else:
                setattr(scene, field, data[field])
    
    # Recalculate word count if content was updated
    if 'content' in data:
        scene.word_count = calculate_word_count(data['content'])
    
    scene.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # Update project's total word count
        update_project_word_count(scene.project_id)
        
        return jsonify({
            'success': True,
            'message': 'Scene updated successfully',
            'scene': scene.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Scene update error: {str(e)}")
        return jsonify({
            'error': 'Scene update failed',
            'message': 'An error occurred while updating the scene'
        }), 500

@scenes_bp.route('/<int:scene_id>', methods=['DELETE'])
@jwt_required()
def delete_scene(scene_id):
    """Delete a scene"""
    current_user_id = get_jwt_identity()
    
    scene = Scene.query.get(scene_id)
    if not scene:
        return jsonify({
            'error': 'Scene not found',
            'message': 'The requested scene was not found'
        }), 404
    
    # Verify project access
    project = verify_project_access(scene.project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have access to this scene'
        }), 403
    
    project_id = scene.project_id
    
    try:
        db.session.delete(scene)
        db.session.commit()
        
        # Update project's total word count
        update_project_word_count(project_id)
        
        return jsonify({
            'success': True,
            'message': 'Scene deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Scene deletion error: {str(e)}")
        return jsonify({
            'error': 'Scene deletion failed',
            'message': 'An error occurred while deleting the scene'
        }), 500

@scenes_bp.route('/reorder', methods=['POST'])
@jwt_required()
def reorder_scenes():
    """Reorder scenes within a project"""
    current_user_id = get_jwt_identity()
    
    try:
        # Validate input
        schema = SceneReorderSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    scene_orders = data['scene_order']
    if not scene_orders:
        return jsonify({
            'error': 'No scenes to reorder',
            'message': 'Please provide scene order data'
        }), 400
    
    # Get first scene to verify project access
    first_scene_id = scene_orders[0]['id']
    first_scene = Scene.query.get(first_scene_id)
    if not first_scene:
        return jsonify({
            'error': 'Scene not found',
            'message': 'One or more scenes were not found'
        }), 404
    
    # Verify project access
    project = verify_project_access(first_scene.project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have access to these scenes'
        }), 403
    
    try:
        # Update scene orders
        for scene_order in scene_orders:
            scene = Scene.query.get(scene_order['id'])
            if scene and scene.project_id == first_scene.project_id:
                scene.order_index = scene_order['order']
                scene.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Scenes reordered successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Scene reordering error: {str(e)}")
        return jsonify({
            'error': 'Scene reordering failed',
            'message': 'An error occurred while reordering scenes'
        }), 500

@scenes_bp.route('/<int:scene_id>/objects', methods=['GET'])
@jwt_required()
def get_scene_objects(scene_id):
    """Get all objects associated with a scene"""
    current_user_id = get_jwt_identity()
    
    scene = Scene.query.get(scene_id)
    if not scene:
        return jsonify({
            'error': 'Scene not found',
            'message': 'The requested scene was not found'
        }), 404
    
    # Verify project access
    project = verify_project_access(scene.project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have access to this scene'
        }), 403
    
    # Get scene objects with their details
    scene_objects = db.session.query(SceneObject, StoryObject).join(
        StoryObject, SceneObject.object_id == StoryObject.id
    ).filter(SceneObject.scene_id == scene_id).all()
    
    objects_data = []
    for scene_obj, story_obj in scene_objects:
        obj_data = story_obj.to_dict()
        obj_data['scene_relationship'] = {
            'role': scene_obj.role,
            'importance_in_scene': scene_obj.importance_in_scene,
            'notes': scene_obj.notes
        }
        objects_data.append(obj_data)
    
    return jsonify({
        'objects': objects_data
    }), 200

@scenes_bp.route('/<int:scene_id>/objects', methods=['POST'])
@jwt_required()
def add_object_to_scene(scene_id):
    """Add a story object to a scene"""
    current_user_id = get_jwt_identity()
    
    scene = Scene.query.get(scene_id)
    if not scene:
        return jsonify({
            'error': 'Scene not found',
            'message': 'The requested scene was not found'
        }), 404
    
    # Verify project access
    project = verify_project_access(scene.project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have access to this scene'
        }), 403
    
    data = request.get_json()
    object_id = data.get('object_id')
    role = data.get('role', 'supporting')
    importance = data.get('importance_in_scene', 'minor')
    notes = data.get('notes', '')
    
    if not object_id:
        return jsonify({
            'error': 'Object ID required',
            'message': 'Please specify an object_id'
        }), 400
    
    # Verify object exists and belongs to the same project
    story_object = StoryObject.query.filter_by(
        id=object_id, 
        project_id=scene.project_id
    ).first()
    
    if not story_object:
        return jsonify({
            'error': 'Object not found',
            'message': 'The specified object was not found in this project'
        }), 404
    
    # Check if relationship already exists
    existing = SceneObject.query.filter_by(
        scene_id=scene_id, 
        object_id=object_id
    ).first()
    
    if existing:
        return jsonify({
            'error': 'Object already in scene',
            'message': 'This object is already associated with this scene'
        }), 400
    
    try:
        # Create scene-object relationship
        scene_object = SceneObject(
            scene_id=scene_id,
            object_id=object_id,
            role=role,
            importance_in_scene=importance,
            notes=notes
        )
        
        db.session.add(scene_object)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Object added to scene successfully',
            'scene_object': scene_object.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Scene object creation error: {str(e)}")
        return jsonify({
            'error': 'Failed to add object to scene',
            'message': 'An error occurred while adding the object to the scene'
        }), 500

@scenes_bp.route('/<int:scene_id>/objects/<int:object_id>', methods=['DELETE'])
@jwt_required()
def remove_object_from_scene(scene_id, object_id):
    """Remove a story object from a scene"""
    current_user_id = get_jwt_identity()
    
    scene = Scene.query.get(scene_id)
    if not scene:
        return jsonify({
            'error': 'Scene not found',
            'message': 'The requested scene was not found'
        }), 404
    
    # Verify project access
    project = verify_project_access(scene.project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have access to this scene'
        }), 403
    
    # Find scene-object relationship
    scene_object = SceneObject.query.filter_by(
        scene_id=scene_id, 
        object_id=object_id
    ).first()
    
    if not scene_object:
        return jsonify({
            'error': 'Object not found in scene',
            'message': 'This object is not associated with this scene'
        }), 404
    
    try:
        db.session.delete(scene_object)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Object removed from scene successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Scene object removal error: {str(e)}")
        return jsonify({
            'error': 'Failed to remove object from scene',
            'message': 'An error occurred while removing the object from the scene'
        }), 500

def update_project_word_count(project_id):
    """Update project's total word count based on scenes"""
    try:
        total_words = db.session.query(db.func.sum(Scene.word_count)).filter_by(
            project_id=project_id
        ).scalar() or 0
        
        project = Project.query.get(project_id)
        if project:
            project.current_word_count = total_words
            project.updated_at = datetime.utcnow()
            db.session.commit()
    
    except Exception as e:
        current_app.logger.error(f"Project word count update error: {str(e)}")
        db.session.rollback()