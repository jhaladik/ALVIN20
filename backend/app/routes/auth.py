# backend/app/routes/auth.py - FIXED VERSION (Remove problematic dependencies)
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt
)
from marshmallow import Schema, fields, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, blacklisted_tokens

auth_bp = Blueprint('auth', __name__)

# ✅ FIXED: Simplified User model for immediate functionality
class User:
    def __init__(self, id=None, username=None, email=None, full_name=None, plan='free', tokens_limit=1000):
        self.id = id or 1
        self.username = username
        self.email = email
        self.full_name = full_name
        self.plan = plan
        self.tokens_limit = tokens_limit
        self.tokens_used = 0
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.password_hash = None
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'plan': self.plan,
            'tokens_used': self.tokens_used,
            'tokens_limit': self.tokens_limit,
            'tokens_remaining': self.tokens_limit - self.tokens_used,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_remaining_tokens(self):
        return max(0, self.tokens_limit - self.tokens_used)

# ✅ FIXED: In-memory user storage for development
demo_users = {}

# Create demo user
demo_user = User(
    id=1,
    username='demo',
    email='demo@alvin.ai',
    full_name='Demo User',
    plan='free',
    tokens_limit=1000
)
demo_user.set_password('demo123')
demo_users['demo@alvin.ai'] = demo_user

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
    if data['email'] in demo_users:
        return jsonify({
            'error': 'Email already registered',
            'message': 'This email is already associated with an account'
        }), 400
    
    # Create new user
    user_id = len(demo_users) + 1
    token_limit = current_app.config.get('TOKEN_LIMITS', {}).get('free', 1000)
    
    user = User(
        id=user_id,
        username=data['username'],
        email=data['email'],
        full_name=data.get('full_name'),
        plan='free',
        tokens_limit=token_limit
    )
    user.set_password(data['password'])
    
    # Store user
    demo_users[data['email']] = user
    
    # Create JWT tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'success': True,
        'message': 'User created successfully',
        'user': user.to_dict(),
        'token': access_token,           # For frontend compatibility
        'access_token': access_token,    # Standard JWT field
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
    }), 201

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
    user = demo_users.get(data['email'])
    
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
    user.updated_at = datetime.utcnow()
    
    # Create JWT tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': user.to_dict(),
        'token': access_token,           # For frontend compatibility
        'access_token': access_token,    # Standard JWT field
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
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
    
    # Find user by ID
    user = None
    for u in demo_users.values():
        if u.id == int(current_user_id):
            user = u
            break
    
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
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    current_user_id = get_jwt_identity()
    
    # Find user by ID
    user = None
    for u in demo_users.values():
        if u.id == int(current_user_id):
            user = u
            break
    
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
    
    # Find user by ID
    user = None
    for u in demo_users.values():
        if u.id == int(current_user_id):
            user = u
            break
    
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
    
    # Update user fields
    if 'username' in data:
        user.username = data['username']
    if 'full_name' in data:
        user.full_name = data['full_name']
    
    user.updated_at = datetime.utcnow()
    
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify if the current token is valid"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find user by ID
        user = None
        for u in demo_users.values():
            if u.id == int(current_user_id):
                user = u
                break
        
        if not user:
            return jsonify({
                'valid': False, 
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'valid': True,
            'user_id': current_user_id,
            'email': user.email,
            'user': user.to_dict(),
            'message': 'Token is valid'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token verification error: {str(e)}")
        return jsonify({
            'valid': False, 
            'message': 'Token verification failed'
        }), 500

# Health check for auth blueprint
@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Auth blueprint status"""
    return jsonify({
        'auth_blueprint': 'operational',
        'demo_users_count': len(demo_users),
        'demo_account': 'demo@alvin.ai available',
        'message': 'Authentication system ready'
    }), 200