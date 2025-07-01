# app/routes/objects.py - ALVIN Story Objects Routes
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from sqlalchemy import desc, asc, or_
from app import db
from app.models import User, Project, StoryObject, SceneObject, Scene

objects_bp = Blueprint('objects', __name__)

# Validation schemas
class StoryObjectCreateSchema(Schema):
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 1 and len(x) <= 100)
    object_type = fields.Str(required=True, validate=lambda x: x in [
        'character', 'location', 'object', 'concept', 'theme', 'organization'
    ])
    description = fields.Str(missing='')
    importance = fields.Str(missing='medium', validate=lambda x: x in ['low', 'medium', 'high', 'critical'])
    character_role = fields.Str(missing=None, validate=lambda x: x is None or x in [
        'protagonist', 'antagonist', 'supporting', 'minor', 'narrator', 'mentor', 'foil'
    ])
    symbolic_meaning = fields.Str(missing='')
    attributes = fields.Dict(missing={})
    project_id = fields.Str(required=True)

class StoryObjectUpdateSchema(Schema):
    name = fields.Str(validate=lambda x: len(x.strip()) >= 1 and len(x) <= 100)
    object_type = fields.Str(validate=lambda x: x in [
        'character', 'location', 'object', 'concept', 'theme', 'organization'
    ])
    description = fields.Str()
    importance = fields.Str(validate=lambda x: x in ['low', 'medium', 'high', 'critical'])
    status = fields.Str(validate=lambda x: x in ['active', 'inactive', 'removed'])
    character_role = fields.Str(allow_none=True, validate=lambda x: x is None or x in [
        'protagonist', 'antagonist', 'supporting', 'minor', 'narrator', 'mentor', 'foil'
    ])
    symbolic_meaning = fields.Str()
    attributes = fields.Dict()

class RelationshipSchema(Schema):
    object_id_1 = fields.Int(required=True)
    object_id_2 = fields.Int(required=True)
    relationship_type = fields.Str(required=True, validate=lambda x: x in [
        'conflict', 'alliance', 'family', 'romantic', 'mentor', 'rival', 'friend', 'enemy', 'neutral'
    ])
    description = fields.Str(missing='')
    intensity = fields.Float(missing=0.5, validate=lambda x: 0.0 <= x <= 1.0)

def verify_project_access(project_id, user_id):
    """Verify user has access to the project"""
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    return project

@objects_bp.route('', methods=['GET'])
@jwt_required()
def get_objects():
    """Get story objects with filtering and pagination"""
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
    per_page = min(request.args.get('limit', 50), 100)
    sort_by = request.args.get('sort', 'name')
    sort_order = request.args.get('order', 'asc')
    object_type = request.args.get('type', '').strip()
    importance = request.args.get('importance', '').strip()
    status = request.args.get('status', 'active').strip()
    search = request.args.get('search', '').strip()
    
    # Base query
    query = StoryObject.query.filter_by(project_id=project_id)
    
    # Apply filters
    if object_type:
        query = query.filter_by(object_type=object_type)
    
    if importance:
        query = query.filter_by(importance=importance)
    
    if status:
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(
            or_(
                StoryObject.name.ilike(f'%{search}%'),
                StoryObject.description.ilike(f'%{search}%'),
                StoryObject.symbolic_meaning.ilike(f'%{search}%')
            )
        )
    
    # Apply sorting
    sort_column = getattr(StoryObject, sort_by, StoryObject.name)
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
        'objects': [obj.to_dict() for obj in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

@objects_bp.route('', methods=['POST'])
@jwt_required()
def create_object():
    """Create a new story object"""
    current_user_id = get_jwt_identity()
    
    try:
        # Validate input
        schema = StoryObjectCreateSchema()
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
    
    # Check for duplicate names within the project
    existing = StoryObject.query.filter_by(
        project_id=data['project_id'],
        name=data['name'].strip(),
        object_type=data['object_type']
    ).first()
    
    if existing:
        return jsonify({
            'error': 'Object already exists',
            'message': f'A {data["object_type"]} named "{data["name"]}" already exists in this project'
        }), 400
    
    # Create story object
    story_object = StoryObject(
        name=data['name'].strip(),
        object_type=data['object_type'],
        description=data.get('description', ''),
        importance=data.get('importance', 'medium'),
        character_role=data.get('character_role') if data['object_type'] == 'character' else None,
        symbolic_meaning=data.get('symbolic_meaning', ''),
        attributes=data.get('attributes', {}),
        project_id=data['project_id']
    )
    
    try:
        db.session.add(story_object)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Story object created successfully',
            'object': story_object.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Story object creation error: {str(e)}")
        return jsonify({
            'error': 'Object creation failed',
            'message': 'An error occurred while creating the story object'
        }), 500

@objects_bp.route('/<int:object_id>', methods=['GET'])
@jwt_required()
def get_object(object_id):
    """Get a specific story object"""
    current_user_id = get_jwt_identity()
    
    story_object = StoryObject.query.get(object_id)
    if not story_object:
        return jsonify({
            'error': 'Object not found',
            'message': 'The requested story object was not found'
        }), 404
    
    # Verify project access
    project = verify_project_access(story_object.project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have access to this story object'
        }), 403
    
    # Get scenes where this object appears
    scene_appearances = db.session.query(Scene, SceneObject).join(
        SceneObject, Scene.id == SceneObject.scene_id
    ).filter(SceneObject.object_id == object_id).order_by(Scene.order_index).all()
    
    object_data = story_object.to_dict()
    object_data['scene_appearances'] = []
    
    for scene, scene_obj in scene_appearances:
        appearance = {
            'scene_id': scene.id,
            'scene_title': scene.title,
            'scene_order': scene.order_index,
            'role': scene_obj.role,
            'importance_in_scene': scene_obj.importance_in_scene,
            'notes': scene_obj.notes
        }
        object_data['scene_appearances'].append(appearance)
    
    return jsonify({
        'object': object_data
    }), 200

@objects_bp.route('/<int:object_id>', methods=['PUT'])
@jwt_required()
def update_object(object_id):
    """Update a story object"""
    current_user_id = get_jwt_identity()
    
    story_object = StoryObject.query.get(object_id)
    if not story_object:
        return jsonify({
            'error': 'Object not found',
            'message': 'The requested story object was not found'
        }), 404
    
    # Verify project access
    project = verify_project_access(story_object.project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have access to this story object'
        }), 403
    
    try:
        # Validate input
        schema = StoryObjectUpdateSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Check for duplicate names if name is being changed
    if 'name' in data and data['name'].strip() != story_object.name:
        object_type = data.get('object_type', story_object.object_type)
        existing = StoryObject.query.filter_by(
            project_id=story_object.project_id,
            name=data['name'].strip(),
            object_type=object_type
        ).filter(StoryObject.id != object_id).first()
        
        if existing:
            return jsonify({
                'error': 'Object name already exists',
                'message': f'A {object_type} named "{data["name"]}" already exists in this project'
            }), 400
    
    # Update object fields
    update_fields = [
        'name', 'object_type', 'description', 'importance', 
        'status', 'character_role', 'symbolic_meaning', 'attributes'
    ]
    
    for field in update_fields:
        if field in data:
            if field == 'name' and data[field]:
                setattr(story_object, field, data[field].strip())
            elif field == 'character_role':
                # Only set character_role for character objects
                if data.get('object_type', story_object.object_type) == 'character':
                    setattr(story_object, field, data[field])
                else:
                    setattr(story_object, field, None)
            else:
                setattr(story_object, field, data[field])
    
    story_object.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Story object updated successfully',
            'object': story_object.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Story object update error: {str(e)}")
        return jsonify({
            'error': 'Object update failed',
            'message': 'An error occurred while updating the story object'
        }), 500

@objects_bp.route('/<int:object_id>', methods=['DELETE'])
@jwt_required()
def delete_object(object_id):
    """Delete a story object"""
    current_user_id = get_jwt_identity()
    
    story_object = StoryObject.query.get(object_id)
    if not story_object:
        return jsonify({
            'error': 'Object not found',
            'message': 'The requested story object was not found'
        }), 404
    
    # Verify project access
    project = verify_project_access(story_object.project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have access to this story object'
        }), 403
    
    try:
        db.session.delete(story_object)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Story object deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Story object deletion error: {str(e)}")
        return jsonify({
            'error': 'Object deletion failed',
            'message': 'An error occurred while deleting the story object'
        }), 500

@objects_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_objects_stats():
    """Get statistics about story objects in a project"""
    current_user_id = get_jwt_identity()
    
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
    
    # Calculate statistics
    total_objects = StoryObject.query.filter_by(project_id=project_id, status='active').count()
    
    # Count by type
    type_counts = {}
    object_types = ['character', 'location', 'object', 'concept', 'theme', 'organization']
    for obj_type in object_types:
        count = StoryObject.query.filter_by(
            project_id=project_id, 
            object_type=obj_type, 
            status='active'
        ).count()
        type_counts[obj_type] = count
    
    # Count by importance
    importance_counts = {}
    importance_levels = ['low', 'medium', 'high', 'critical']
    for importance in importance_levels:
        count = StoryObject.query.filter_by(
            project_id=project_id, 
            importance=importance, 
            status='active'
        ).count()
        importance_counts[importance] = count
    
    # Character role distribution
    character_roles = {}
    if type_counts['character'] > 0:
        role_types = ['protagonist', 'antagonist', 'supporting', 'minor', 'narrator', 'mentor', 'foil']
        for role in role_types:
            count = StoryObject.query.filter_by(
                project_id=project_id,
                object_type='character',
                character_role=role,
                status='active'
            ).count()
            if count > 0:
                character_roles[role] = count
    
    return jsonify({
        'stats': {
            'total_objects': total_objects,
            'by_type': type_counts,
            'by_importance': importance_counts,
            'character_roles': character_roles
        }
    }), 200

@objects_bp.route('/bulk-import', methods=['POST'])
@jwt_required()
def bulk_import_objects():
    """Import multiple story objects at once"""
    current_user_id = get_jwt_identity()
    
    data = request.get_json()
    project_id = data.get('project_id')
    objects_data = data.get('objects', [])
    
    if not project_id:
        return jsonify({
            'error': 'Project ID required',
            'message': 'Please specify a project_id'
        }), 400
    
    if not objects_data:
        return jsonify({
            'error': 'No objects provided',
            'message': 'Please provide objects to import'
        }), 400
    
    # Verify project access
    project = verify_project_access(project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    try:
        created_objects = []
        errors = []
        
        for i, obj_data in enumerate(objects_data):
            try:
                # Validate each object
                schema = StoryObjectCreateSchema()
                obj_data['project_id'] = project_id
                validated_data = schema.load(obj_data)
                
                # Check for duplicates
                existing = StoryObject.query.filter_by(
                    project_id=project_id,
                    name=validated_data['name'].strip(),
                    object_type=validated_data['object_type']
                ).first()
                
                if existing:
                    errors.append({
                        'index': i,
                        'name': validated_data['name'],
                        'error': 'Object already exists'
                    })
                    continue
                
                # Create object
                story_object = StoryObject(
                    name=validated_data['name'].strip(),
                    object_type=validated_data['object_type'],
                    description=validated_data.get('description', ''),
                    importance=validated_data.get('importance', 'medium'),
                    character_role=validated_data.get('character_role') if validated_data['object_type'] == 'character' else None,
                    symbolic_meaning=validated_data.get('symbolic_meaning', ''),
                    attributes=validated_data.get('attributes', {}),
                    project_id=project_id
                )
                
                db.session.add(story_object)
                created_objects.append(story_object)
                
            except ValidationError as err:
                errors.append({
                    'index': i,
                    'name': obj_data.get('name', 'Unknown'),
                    'error': f'Validation error: {err.messages}'
                })
                continue
        
        # Commit all successful objects
        if created_objects:
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully imported {len(created_objects)} objects',
            'created_count': len(created_objects),
            'error_count': len(errors),
            'created_objects': [obj.to_dict() for obj in created_objects],
            'errors': errors
        }), 201 if created_objects else 400
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Bulk import error: {str(e)}")
        return jsonify({
            'error': 'Bulk import failed',
            'message': 'An error occurred while importing objects'
        }), 500

@objects_bp.route('/search', methods=['GET'])
@jwt_required()
def search_objects():
    """Advanced search for story objects across projects"""
    current_user_id = get_jwt_identity()
    
    # Query parameters
    query_text = request.args.get('q', '').strip()
    project_id = request.args.get('project_id')
    object_type = request.args.get('type')
    limit = min(request.args.get('limit', 20, type=int), 100)
    
    if not query_text:
        return jsonify({
            'error': 'Search query required',
            'message': 'Please provide a search query'
        }), 400
    
    # Base query - only user's projects
    base_query = db.session.query(StoryObject).join(
        Project, StoryObject.project_id == Project.id
    ).filter(Project.user_id == current_user_id)
    
    # Apply filters
    if project_id:
        base_query = base_query.filter(StoryObject.project_id == project_id)
    
    if object_type:
        base_query = base_query.filter(StoryObject.object_type == object_type)
    
    # Apply search
    search_query = base_query.filter(
        or_(
            StoryObject.name.ilike(f'%{query_text}%'),
            StoryObject.description.ilike(f'%{query_text}%'),
            StoryObject.symbolic_meaning.ilike(f'%{query_text}%')
        )
    ).filter(StoryObject.status == 'active')
    
    # Get results
    objects = search_query.limit(limit).all()
    
    # Format results with project context
    results = []
    for obj in objects:
        obj_data = obj.to_dict()
        project = Project.query.get(obj.project_id)
        obj_data['project_title'] = project.title if project else 'Unknown Project'
        results.append(obj_data)
    
    return jsonify({
        'results': results,
        'total_found': search_query.count(),
        'search_query': query_text
    }), 200