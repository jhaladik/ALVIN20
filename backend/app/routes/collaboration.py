# app/routes/collaboration.py - ALVIN Collaboration Routes
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from sqlalchemy import desc, or_
from app import db
from app.models import User, Project, ProjectCollaborator, Comment, Scene

collaboration_bp = Blueprint('collaboration', __name__)

# Validation schemas
class InviteCollaboratorSchema(Schema):
    email = fields.Email(required=True)
    role = fields.Str(missing='editor', validate=lambda x: x in ['owner', 'editor', 'viewer', 'commenter'])
    message = fields.Str(missing='')

class UpdateCollaboratorSchema(Schema):
    role = fields.Str(required=True, validate=lambda x: x in ['owner', 'editor', 'viewer', 'commenter'])
    permissions = fields.Dict(missing={})

class CommentCreateSchema(Schema):
    content = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 1 and len(x) <= 2000)
    target_type = fields.Str(required=True, validate=lambda x: x in ['project', 'scene', 'story_object'])
    target_id = fields.Str(required=True)
    parent_comment_id = fields.Int(missing=None)

class CommentUpdateSchema(Schema):
    content = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 1 and len(x) <= 2000)
    is_resolved = fields.Bool(missing=None)

def verify_project_access(project_id, user_id, required_role=None):
    """Verify user has access to the project with optional role check"""
    # Check if user is the owner
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if project:
        return project, 'owner'
    
    # Check if user is a collaborator
    collaborator = ProjectCollaborator.query.filter_by(
        project_id=project_id, 
        user_id=user_id, 
        status='active'
    ).first()
    
    if collaborator:
        project = Project.query.get(project_id)
        if required_role and not has_permission(collaborator.role, required_role):
            return None, None
        return project, collaborator.role
    
    return None, None

def has_permission(user_role, required_role):
    """Check if user role has required permission"""
    role_hierarchy = {
        'owner': 4,
        'editor': 3,
        'commenter': 2,
        'viewer': 1
    }
    
    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)

@collaboration_bp.route('/projects/<project_id>/collaborators', methods=['GET'])
@jwt_required()
def get_collaborators(project_id):
    """Get all collaborators for a project"""
    current_user_id = get_jwt_identity()
    
    # Verify project access
    project, user_role = verify_project_access(project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found or you do not have access'
        }), 404
    
    # Get project owner
    owner = User.query.get(project.user_id)
    collaborators_data = []
    
    if owner:
        collaborators_data.append({
            'user_id': owner.id,
            'username': owner.username,
            'email': owner.email,
            'full_name': owner.full_name,
            'avatar_url': owner.avatar_url,
            'role': 'owner',
            'status': 'active',
            'joined_at': project.created_at.isoformat() if project.created_at else None,
            'last_access': owner.last_login.isoformat() if owner.last_login else None,
            'is_owner': True
        })
    
    # Get collaborators
    collaborators = db.session.query(ProjectCollaborator, User).join(
        User, ProjectCollaborator.user_id == User.id
    ).filter(ProjectCollaborator.project_id == project_id).all()
    
    for collab, user in collaborators:
        collaborators_data.append({
            'collaboration_id': collab.id,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'avatar_url': user.avatar_url,
            'role': collab.role,
            'status': collab.status,
            'permissions': collab.permissions,
            'invited_at': collab.invited_at.isoformat() if collab.invited_at else None,
            'joined_at': collab.joined_at.isoformat() if collab.joined_at else None,
            'last_access': collab.last_access.isoformat() if collab.last_access else None,
            'is_owner': False
        })
    
    return jsonify({
        'collaborators': collaborators_data,
        'your_role': user_role
    }), 200

@collaboration_bp.route('/projects/<project_id>/invite', methods=['POST'])
@jwt_required()
def invite_collaborator(project_id):
    """Invite a collaborator to a project"""
    current_user_id = get_jwt_identity()
    
    # Verify project access and permission to invite
    project, user_role = verify_project_access(project_id, current_user_id, 'editor')
    if not project:
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have permission to invite collaborators to this project'
        }), 403
    
    try:
        # Validate input
        schema = InviteCollaboratorSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Find user by email
    invited_user = User.query.filter_by(email=data['email']).first()
    if not invited_user:
        return jsonify({
            'error': 'User not found',
            'message': 'No user found with that email address'
        }), 404
    
    # Check if user is the project owner
    if invited_user.id == project.user_id:
        return jsonify({
            'error': 'Cannot invite owner',
            'message': 'The project owner cannot be invited as a collaborator'
        }), 400
    
    # Check if user is already a collaborator
    existing_collaboration = ProjectCollaborator.query.filter_by(
        project_id=project_id,
        user_id=invited_user.id
    ).first()
    
    if existing_collaboration:
        if existing_collaboration.status == 'active':
            return jsonify({
                'error': 'Already collaborating',
                'message': 'This user is already a collaborator on this project'
            }), 400
        elif existing_collaboration.status == 'invited':
            return jsonify({
                'error': 'Already invited',
                'message': 'This user has already been invited to this project'
            }), 400
    
    try:
        # Create invitation
        invitation_token = str(uuid.uuid4())
        collaboration = ProjectCollaborator(
            project_id=project_id,
            user_id=invited_user.id,
            role=data['role'],
            status='invited',
            invitation_token=invitation_token,
            invited_by=current_user_id,
            invited_at=datetime.utcnow()
        )
        
        db.session.add(collaboration)
        db.session.commit()
        
        # In a real implementation, send email notification here
        
        return jsonify({
            'success': True,
            'message': 'Invitation sent successfully',
            'collaboration': {
                'id': collaboration.id,
                'user_id': invited_user.id,
                'username': invited_user.username,
                'email': invited_user.email,
                'role': collaboration.role,
                'status': collaboration.status,
                'invited_at': collaboration.invited_at.isoformat()
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Collaboration invitation error: {str(e)}")
        return jsonify({
            'error': 'Invitation failed',
            'message': 'An error occurred while sending the invitation'
        }), 500

@collaboration_bp.route('/projects/<project_id>/collaborators/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_collaborator(project_id, user_id):
    """Update a collaborator's role and permissions"""
    current_user_id = get_jwt_identity()
    
    # Verify project access and permission to manage collaborators
    project, user_role = verify_project_access(project_id, current_user_id, 'editor')
    if not project:
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have permission to manage collaborators on this project'
        }), 403
    
    # Find the collaboration
    collaboration = ProjectCollaborator.query.filter_by(
        project_id=project_id,
        user_id=user_id
    ).first()
    
    if not collaboration:
        return jsonify({
            'error': 'Collaborator not found',
            'message': 'The specified collaborator was not found'
        }), 404
    
    try:
        # Validate input
        schema = UpdateCollaboratorSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    try:
        # Update collaboration
        collaboration.role = data['role']
        collaboration.permissions = data.get('permissions', {})
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Collaborator updated successfully',
            'collaboration': collaboration.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Collaborator update error: {str(e)}")
        return jsonify({
            'error': 'Update failed',
            'message': 'An error occurred while updating the collaborator'
        }), 500

@collaboration_bp.route('/projects/<project_id>/collaborators/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_collaborator(project_id, user_id):
    """Remove a collaborator from a project"""
    current_user_id = get_jwt_identity()
    
    # Verify project access and permission to manage collaborators
    project, user_role = verify_project_access(project_id, current_user_id, 'editor')
    if not project:
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have permission to manage collaborators on this project'
        }), 403
    
    # Find the collaboration
    collaboration = ProjectCollaborator.query.filter_by(
        project_id=project_id,
        user_id=user_id
    ).first()
    
    if not collaboration:
        return jsonify({
            'error': 'Collaborator not found',
            'message': 'The specified collaborator was not found'
        }), 404
    
    try:
        db.session.delete(collaboration)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Collaborator removed successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Collaborator removal error: {str(e)}")
        return jsonify({
            'error': 'Removal failed',
            'message': 'An error occurred while removing the collaborator'
        }), 500

@collaboration_bp.route('/invitations', methods=['GET'])
@jwt_required()
def get_user_invitations():
    """Get pending invitations for the current user"""
    current_user_id = get_jwt_identity()
    
    # Get pending invitations
    invitations = db.session.query(ProjectCollaborator, Project, User).join(
        Project, ProjectCollaborator.project_id == Project.id
    ).join(
        User, ProjectCollaborator.invited_by == User.id
    ).filter(
        ProjectCollaborator.user_id == current_user_id,
        ProjectCollaborator.status == 'invited'
    ).all()
    
    invitations_data = []
    for collab, project, inviter in invitations:
        invitations_data.append({
            'invitation_id': collab.id,
            'project_id': project.id,
            'project_title': project.title,
            'project_description': project.description,
            'role': collab.role,
            'invited_by': {
                'id': inviter.id,
                'username': inviter.username,
                'full_name': inviter.full_name
            },
            'invited_at': collab.invited_at.isoformat() if collab.invited_at else None,
            'invitation_token': collab.invitation_token
        })
    
    return jsonify({
        'invitations': invitations_data
    }), 200

@collaboration_bp.route('/invitations/<int:invitation_id>/accept', methods=['POST'])
@jwt_required()
def accept_invitation(invitation_id):
    """Accept a collaboration invitation"""
    current_user_id = get_jwt_identity()
    
    # Find the invitation
    collaboration = ProjectCollaborator.query.filter_by(
        id=invitation_id,
        user_id=current_user_id,
        status='invited'
    ).first()
    
    if not collaboration:
        return jsonify({
            'error': 'Invitation not found',
            'message': 'The invitation was not found or has already been processed'
        }), 404
    
    try:
        # Accept the invitation
        collaboration.status = 'active'
        collaboration.joined_at = datetime.utcnow()
        collaboration.invitation_token = None  # Clear the token
        
        db.session.commit()
        
        # Get project details
        project = Project.query.get(collaboration.project_id)
        
        return jsonify({
            'success': True,
            'message': 'Invitation accepted successfully',
            'project': project.to_dict() if project else None,
            'role': collaboration.role
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Invitation acceptance error: {str(e)}")
        return jsonify({
            'error': 'Acceptance failed',
            'message': 'An error occurred while accepting the invitation'
        }), 500

@collaboration_bp.route('/invitations/<int:invitation_id>/decline', methods=['POST'])
@jwt_required()
def decline_invitation(invitation_id):
    """Decline a collaboration invitation"""
    current_user_id = get_jwt_identity()
    
    # Find the invitation
    collaboration = ProjectCollaborator.query.filter_by(
        id=invitation_id,
        user_id=current_user_id,
        status='invited'
    ).first()
    
    if not collaboration:
        return jsonify({
            'error': 'Invitation not found',
            'message': 'The invitation was not found or has already been processed'
        }), 404
    
    try:
        # Remove the invitation
        db.session.delete(collaboration)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Invitation declined successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Invitation decline error: {str(e)}")
        return jsonify({
            'error': 'Decline failed',
            'message': 'An error occurred while declining the invitation'
        }), 500

@collaboration_bp.route('/projects/<project_id>/comments', methods=['GET'])
@jwt_required()
def get_comments(project_id):
    """Get comments for a project or specific target"""
    current_user_id = get_jwt_identity()
    
    # Verify project access
    project, user_role = verify_project_access(project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found or you do not have access'
        }), 404
    
    # Query parameters
    target_type = request.args.get('target_type')
    target_id = request.args.get('target_id')
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('limit', current_app.config['COMMENTS_PER_PAGE']), 100)
    
    # Base query
    query = Comment.query.filter_by(project_id=project_id)
    
    # Filter by target if specified
    if target_type and target_id:
        query = query.filter_by(target_type=target_type, target_id=target_id)
    
    # Only get top-level comments (replies will be nested)
    query = query.filter_by(parent_comment_id=None)
    
    # Order by creation date (newest first)
    query = query.order_by(desc(Comment.created_at))
    
    # Paginate
    pagination = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    # Get comments with user details and replies
    comments_data = []
    for comment in pagination.items:
        user = User.query.get(comment.user_id)
        comment_data = comment.to_dict(include_replies=True)
        comment_data['user'] = {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'avatar_url': user.avatar_url
        } if user else None
        
        # Add user details to replies
        for reply in comment_data.get('replies', []):
            reply_user = User.query.get(reply['user_id'])
            reply['user'] = {
                'id': reply_user.id,
                'username': reply_user.username,
                'full_name': reply_user.full_name,
                'avatar_url': reply_user.avatar_url
            } if reply_user else None
        
        comments_data.append(comment_data)
    
    return jsonify({
        'comments': comments_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

@collaboration_bp.route('/projects/<project_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(project_id):
    """Add a comment to a project target"""
    current_user_id = get_jwt_identity()
    
    # Verify project access with commenter permission
    project, user_role = verify_project_access(project_id, current_user_id, 'commenter')
    if not project:
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have permission to comment on this project'
        }), 403
    
    try:
        # Validate input
        schema = CommentCreateSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Validate target exists if it's a scene
    if data['target_type'] == 'scene':
        scene = Scene.query.filter_by(
            id=data['target_id'], 
            project_id=project_id
        ).first()
        if not scene:
            return jsonify({
                'error': 'Scene not found',
                'message': 'The specified scene was not found in this project'
            }), 404
    
    # Validate parent comment if specified
    parent_comment = None
    if data.get('parent_comment_id'):
        parent_comment = Comment.query.filter_by(
            id=data['parent_comment_id'],
            project_id=project_id
        ).first()
        if not parent_comment:
            return jsonify({
                'error': 'Parent comment not found',
                'message': 'The specified parent comment was not found'
            }), 404
    
    try:
        # Create comment
        comment = Comment(
            content=data['content'].strip(),
            target_type=data['target_type'],
            target_id=data['target_id'],
            parent_comment_id=data.get('parent_comment_id'),
            user_id=current_user_id,
            project_id=project_id,
            scene_id=data['target_id'] if data['target_type'] == 'scene' else None
        )
        
        # Set thread position for replies
        if parent_comment:
            max_position = Comment.query.filter_by(
                parent_comment_id=parent_comment.id
            ).count()
            comment.thread_position = max_position + 1
        
        db.session.add(comment)
        db.session.commit()
        
        # Get user details for response
        user = User.query.get(current_user_id)
        comment_data = comment.to_dict()
        comment_data['user'] = {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'avatar_url': user.avatar_url
        } if user else None
        
        return jsonify({
            'success': True,
            'message': 'Comment added successfully',
            'comment': comment_data
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Comment creation error: {str(e)}")
        return jsonify({
            'error': 'Comment creation failed',
            'message': 'An error occurred while adding the comment'
        }), 500

@collaboration_bp.route('/projects/<project_id>/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(project_id, comment_id):
    """Update a comment"""
    current_user_id = get_jwt_identity()
    
    # Verify project access
    project, user_role = verify_project_access(project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found or you do not have access'
        }), 404
    
    # Find the comment
    comment = Comment.query.filter_by(
        id=comment_id,
        project_id=project_id
    ).first()
    
    if not comment:
        return jsonify({
            'error': 'Comment not found',
            'message': 'The specified comment was not found'
        }), 404
    
    # Check if user can edit (owner of comment or project owner/editor)
    if comment.user_id != current_user_id and not has_permission(user_role, 'editor'):
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have permission to edit this comment'
        }), 403
    
    try:
        # Validate input
        schema = CommentUpdateSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    try:
        # Update comment
        comment.content = data['content'].strip()
        comment.is_edited = True
        comment.updated_at = datetime.utcnow()
        
        # Only project owners/editors can resolve comments
        if 'is_resolved' in data and has_permission(user_role, 'editor'):
            comment.is_resolved = data['is_resolved']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Comment updated successfully',
            'comment': comment.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Comment update error: {str(e)}")
        return jsonify({
            'error': 'Comment update failed',
            'message': 'An error occurred while updating the comment'
        }), 500

@collaboration_bp.route('/projects/<project_id>/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(project_id, comment_id):
    """Delete a comment"""
    current_user_id = get_jwt_identity()
    
    # Verify project access
    project, user_role = verify_project_access(project_id, current_user_id)
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found or you do not have access'
        }), 404
    
    # Find the comment
    comment = Comment.query.filter_by(
        id=comment_id,
        project_id=project_id
    ).first()
    
    if not comment:
        return jsonify({
            'error': 'Comment not found',
            'message': 'The specified comment was not found'
        }), 404
    
    # Check if user can delete (owner of comment or project owner/editor)
    if comment.user_id != current_user_id and not has_permission(user_role, 'editor'):
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have permission to delete this comment'
        }), 403
    
    try:
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Comment deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Comment deletion error: {str(e)}")
        return jsonify({
            'error': 'Comment deletion failed',
            'message': 'An error occurred while deleting the comment'
        }), 500