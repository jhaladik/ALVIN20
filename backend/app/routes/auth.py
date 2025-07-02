# app/routes/auth.py - ALVIN Authentication Routes
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt, current_user
)
from marshmallow import Schema, fields, ValidationError
from app import db, blacklisted_tokens
from app.models import User

auth_bp = Blueprint('auth', __name__)

# Validation schemas
class UserRegistrationSchema(Schema):
    username = fields.Str(required=True, validate=lambda x: len(x) >= 3 and len(x) <= 80)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 6)
    full_name = fields.Str(missing=None)

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserProfileUpdateSchema(Schema):
    username = fields.Str(validate=lambda x: len(x) >= 3 and len(x) <= 80)
    full_name = fields.Str(allow_none=True)
    bio = fields.Str(allow_none=True)
    avatar_url = fields.Url(allow_none=True)

class PasswordResetSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=lambda x: len(x) >= 6)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        # Validate input
        schema = UserRegistrationSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'error': 'Email already registered',
            'message': 'This email is already associated with an account'
        }), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'error': 'Username already taken',
            'message': 'Please choose a different username'
        }), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data.get('full_name'),
        plan='free',
        tokens_limit=current_app.config['TOKEN_LIMITS']['free']
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Create JWT tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'user': user.to_dict(),
            'token': access_token,
            'refresh_token': refresh_token
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'error': 'Registration failed',
            'message': 'An error occurred while creating your account'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens"""
    try:
        # Validate input
        schema = UserLoginSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({
            'error': 'Invalid credentials',
            'message': 'Email or password is incorrect'
        }), 401
    
    if not user.is_active:
        return jsonify({
            'error': 'Account disabled',
            'message': 'Your account has been disabled. Please contact support.'
        }), 401
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create JWT tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': user.to_dict(),
        'token': access_token,
        'refresh_token': refresh_token
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user and blacklist token"""
    jti = get_jwt()['jti']
    blacklisted_tokens.add(jti)
    
    return jsonify({
        'success': True,
        'message': 'Successfully logged out'
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'error': 'Invalid user',
            'message': 'User not found or account disabled'
        }), 401
    
    # Create new access token
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'success': True,
        'token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': 'The authenticated user was not found'
        }), 404
    
    return jsonify({
        'user': user.to_dict()
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': 'The authenticated user was not found'
        }), 404
    
    try:
        # Validate input
        schema = UserProfileUpdateSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Check if username is taken (if being updated)
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'error': 'Username already taken',
                'message': 'Please choose a different username'
            }), 400
    
    # Update user fields
    for field in ['username', 'full_name', 'bio', 'avatar_url']:
        if field in data:
            setattr(user, field, data[field])
    
    user.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Profile update error: {str(e)}")
        return jsonify({
            'error': 'Update failed',
            'message': 'An error occurred while updating your profile'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': 'The authenticated user was not found'
        }), 404
    
    try:
        # Validate input
        schema = PasswordResetSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Verify current password
    if not user.check_password(data['current_password']):
        return jsonify({
            'error': 'Invalid password',
            'message': 'Current password is incorrect'
        }), 400
    
    # Update password
    user.set_password(data['new_password'])
    user.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # Blacklist current token to force re-login
        jti = get_jwt()['jti']
        blacklisted_tokens.add(jti)
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully. Please log in again.'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password change error: {str(e)}")
        return jsonify({
            'error': 'Password change failed',
            'message': 'An error occurred while changing your password'
        }), 500

@auth_bp.route('/verify-email', methods=['POST'])
@jwt_required()
def verify_email():
    """Verify user email (placeholder for email verification system)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': 'The authenticated user was not found'
        }), 404
    
    # In a real implementation, this would involve sending an email
    # and verifying a token. For now, we'll just mark as verified.
    user.email_verified = True
    user.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Email verified successfully',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Email verification error: {str(e)}")
        return jsonify({
            'error': 'Verification failed',
            'message': 'An error occurred while verifying your email'
        }), 500

@auth_bp.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    """Delete user account"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': 'The authenticated user was not found'
        }), 404
    
    # Verify password for account deletion
    data = request.get_json()
    if not data or not data.get('password'):
        return jsonify({
            'error': 'Password required',
            'message': 'Please provide your password to delete your account'
        }), 400
    
    if not user.check_password(data['password']):
        return jsonify({
            'error': 'Invalid password',
            'message': 'Password is incorrect'
        }), 400
    
    try:
        # Blacklist current token
        jti = get_jwt()['jti']
        blacklisted_tokens.add(jti)
        
        # Delete user (cascade will handle related records)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Account deletion error: {str(e)}")
        return jsonify({
            'error': 'Deletion failed',
            'message': 'An error occurred while deleting your account'
        }), 500
    
@auth_bp.route('/notification-preferences', methods=['GET', 'PUT'])
@jwt_required()
def notification_preferences():
    """Get or update user notification preferences"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if request.method == 'GET':
        # Return default preferences for now
        return jsonify({
            'email_notifications': True,
            'project_updates': True,
            'collaboration_alerts': True,
            'marketing_emails': False
        }), 200
    
    elif request.method == 'PUT':
        # Update preferences (placeholder)
        data = request.get_json() or {}
        return jsonify({
            'success': True,
            'message': 'Notification preferences updated',
            'preferences': data
        }), 200

@auth_bp.route('/api-keys', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def api_keys():
    """Manage user API keys"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if request.method == 'GET':
        # Return empty API keys for now
        return jsonify({
            'api_keys': [],
            'count': 0,
            'message': 'API key management coming soon'
        }), 200
    
    elif request.method == 'POST':
        # Create API key (placeholder)
        return jsonify({
            'success': True,
            'message': 'API key creation coming soon',
            'api_key': None
        }), 200
    
    elif request.method == 'DELETE':
        # Delete API key (placeholder)
        return jsonify({
            'success': True,
            'message': 'API key deletion coming soon'
        }), 200
