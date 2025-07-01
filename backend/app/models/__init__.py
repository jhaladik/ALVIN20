# app/models/__init__.py - ALVIN Database Models
import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from .user import User
from .project import Project, Scene, StoryObject
from .billing import BillingPlan, UserSubscription
from .analytics import TokenUsageLog

__all__ = [
    'User',
    'Project', 
    'Scene', 
    'StoryObject',
    'BillingPlan', 
    'UserSubscription',
    'TokenUsageLog'
]

class User(db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    
    # Subscription and tokens
    plan = db.Column(db.String(20), default='free', index=True)
    tokens_used = db.Column(db.Integer, default=0)
    tokens_limit = db.Column(db.Integer, default=1000)
    
    # Profile information
    full_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(200))
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = db.relationship('Project', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    token_usage_logs = db.relationship('TokenUsageLog', backref='user', lazy='dynamic')
    subscriptions = db.relationship('UserSubscription', backref='user', lazy='dynamic')
    collaborations = db.relationship('ProjectCollaborator', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_remaining_tokens(self):
        """Get remaining tokens for the user"""
        return max(0, self.tokens_limit - self.tokens_used)
    
    def can_afford_tokens(self, cost):
        """Check if user can afford token cost"""
        return self.get_remaining_tokens() >= cost
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'plan': self.plan,
            'tokens_used': self.tokens_used,
            'tokens_limit': self.tokens_limit,
            'tokens_remaining': self.get_remaining_tokens(),
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Project(db.Model):
    """Project model for story projects"""
    __tablename__ = 'project'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Story metadata
    genre = db.Column(db.String(50), index=True)
    current_phase = db.Column(db.String(20), default='idea', index=True)  # idea, expand, story
    target_word_count = db.Column(db.Integer)
    current_word_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')  # active, paused, completed, archived
    
    # AI analysis data
    attributes = db.Column(db.JSON)  # Flexible JSON storage for AI-generated attributes
    tone = db.Column(db.String(50))
    target_audience = db.Column(db.String(50))
    estimated_scope = db.Column(db.String(50))
    marketability = db.Column(db.Integer)  # 1-5 score
    
    # Original data
    original_idea = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # Relationships
    scenes = db.relationship('Scene', backref='project', lazy='dynamic', cascade='all, delete-orphan', order_by='Scene.order_index')
    story_objects = db.relationship('StoryObject', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    token_usage_logs = db.relationship('TokenUsageLog', backref='project', lazy='dynamic')
    collaborators = db.relationship('ProjectCollaborator', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='project', lazy='dynamic')
    
    def get_progress_percentage(self):
        """Calculate project progress based on phase and scenes"""
        if self.current_phase == 'idea':
            return 10
        elif self.current_phase == 'expand':
            scene_count = self.scenes.count()
            if scene_count == 0:
                return 25
            elif scene_count < 5:
                return 25 + (scene_count * 10)
            else:
                return 75
        elif self.current_phase == 'story':
            if self.current_word_count == 0:
                return 80
            elif self.target_word_count and self.current_word_count >= self.target_word_count:
                return 100
            elif self.target_word_count:
                return 80 + int((self.current_word_count / self.target_word_count) * 20)
            else:
                return 90
        return 0
    
    def to_dict(self, include_scenes=False, include_objects=False):
        """Convert project to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'genre': self.genre,
            'current_phase': self.current_phase,
            'target_word_count': self.target_word_count,
            'current_word_count': self.current_word_count,
            'status': self.status,
            'attributes': self.attributes,
            'tone': self.tone,
            'target_audience': self.target_audience,
            'estimated_scope': self.estimated_scope,
            'marketability': self.marketability,
            'original_idea': self.original_idea,
            'progress': self.get_progress_percentage(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }
        
        if include_scenes:
            data['scenes'] = [scene.to_dict() for scene in self.scenes.all()]
        
        if include_objects:
            data['story_objects'] = [obj.to_dict() for obj in self.story_objects.all()]
        
        return data

class Scene(db.Model):
    """Scene model for story scenes"""
    __tablename__ = 'scene'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)  # The actual scene content
    
    # Scene metadata
    scene_type = db.Column(db.String(50), index=True)  # opening, inciting, development, climax, resolution
    order_index = db.Column(db.Integer, nullable=False, index=True)
    emotional_intensity = db.Column(db.Float)  # 0.0 to 1.0
    word_count = db.Column(db.Integer, default=0)
    
    # AI analysis
    analysis_data = db.Column(db.JSON)  # Store AI analysis results
    suggestions = db.Column(db.JSON)  # AI suggestions for improvement
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, completed, needs_review
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False, index=True)
    
    # Relationships
    scene_objects = db.relationship('SceneObject', backref='scene', lazy='dynamic', cascade='all, delete-orphan')
    token_usage_logs = db.relationship('TokenUsageLog', backref='scene', lazy='dynamic')
    comments = db.relationship('Comment', backref='scene', lazy='dynamic')
    
    def to_dict(self, include_objects=False):
        """Convert scene to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'scene_type': self.scene_type,
            'order_index': self.order_index,
            'emotional_intensity': self.emotional_intensity,
            'word_count': self.word_count,
            'analysis_data': self.analysis_data,
            'suggestions': self.suggestions,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'project_id': self.project_id
        }
        
        if include_objects:
            data['scene_objects'] = [so.to_dict() for so in self.scene_objects.all()]
        
        return data

class StoryObject(db.Model):
    """Story object model for characters, locations, items, etc."""
    __tablename__ = 'story_object'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    object_type = db.Column(db.String(20), nullable=False, index=True)  # character, location, object, concept
    description = db.Column(db.Text)
    
    # Metadata
    importance = db.Column(db.String(20), default='medium', index=True)  # low, medium, high, critical
    status = db.Column(db.String(20), default='active', index=True)  # active, inactive, removed
    attributes = db.Column(db.JSON)  # Flexible storage for object-specific data
    
    # Story integration
    first_appearance = db.Column(db.Integer)  # Scene order where it first appears
    symbolic_meaning = db.Column(db.Text)
    character_role = db.Column(db.String(50))  # For characters: protagonist, antagonist, supporting, etc.
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False, index=True)
    
    # Relationships
    scene_objects = db.relationship('SceneObject', backref='story_object', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert story object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'object_type': self.object_type,
            'description': self.description,
            'importance': self.importance,
            'status': self.status,
            'attributes': self.attributes,
            'first_appearance': self.first_appearance,
            'symbolic_meaning': self.symbolic_meaning,
            'character_role': self.character_role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'project_id': self.project_id
        }

class SceneObject(db.Model):
    """Many-to-many relationship between scenes and story objects"""
    __tablename__ = 'scene_object'
    
    id = db.Column(db.Integer, primary_key=True)
    scene_id = db.Column(db.Integer, db.ForeignKey('scene.id'), nullable=False, index=True)
    object_id = db.Column(db.Integer, db.ForeignKey('story_object.id'), nullable=False, index=True)
    
    # Relationship metadata
    role = db.Column(db.String(20))  # main, supporting, background, mentioned
    importance_in_scene = db.Column(db.String(20))  # critical, important, minor
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert scene object relationship to dictionary"""
        return {
            'id': self.id,
            'scene_id': self.scene_id,
            'object_id': self.object_id,
            'role': self.role,
            'importance_in_scene': self.importance_in_scene,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class TokenUsageLog(db.Model):
    """Log for tracking AI token usage"""
    __tablename__ = 'token_usage_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    operation_type = db.Column(db.String(50), nullable=False, index=True)
    
    # Token details
    input_tokens = db.Column(db.Integer, default=0)
    output_tokens = db.Column(db.Integer, default=0)
    total_cost = db.Column(db.Integer, nullable=False)  # Total cost in tokens
    multiplier = db.Column(db.Float, default=1.0)  # Cost multiplier for different operations
    
    # Context
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), index=True)
    scene_id = db.Column(db.Integer, db.ForeignKey('scene.id'), index=True)
    operation_metadata = db.Column(db.JSON)  # Additional operation details
    
    # AI model details
    ai_model_used = db.Column(db.String(50))
    response_time_ms = db.Column(db.Integer)
    
    # Billing
    billable = db.Column(db.Boolean, default=True)
    billed_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert token usage log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'operation_type': self.operation_type,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_cost': self.total_cost,
            'multiplier': self.multiplier,
            'project_id': self.project_id,
            'scene_id': self.scene_id,
            'operation_metadata': self.operation_metadata,
            'ai_model_used': self.ai_model_used,
            'response_time_ms': self.response_time_ms,
            'billable': self.billable,
            'billed_at': self.billed_at.isoformat() if self.billed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BillingPlan(db.Model):
    """Billing plans model"""
    __tablename__ = 'billing_plan'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    
    # Limits
    monthly_token_limit = db.Column(db.Integer, nullable=False)
    max_projects = db.Column(db.Integer)
    max_collaborators = db.Column(db.Integer)
    
    # Pricing
    monthly_price_cents = db.Column(db.Integer, default=0)
    token_overage_price_per_1k_cents = db.Column(db.Integer)
    
    # Features
    features = db.Column(db.JSON)  # List of enabled features
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('UserSubscription', backref='plan', lazy='dynamic')
    
    def to_dict(self):
        """Convert billing plan to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'monthly_token_limit': self.monthly_token_limit,
            'max_projects': self.max_projects,
            'max_collaborators': self.max_collaborators,
            'monthly_price_cents': self.monthly_price_cents,
            'monthly_price_dollars': self.monthly_price_cents / 100 if self.monthly_price_cents else 0,
            'token_overage_price_per_1k_cents': self.token_overage_price_per_1k_cents,
            'features': self.features,
            'is_active': self.is_active,
            'is_public': self.is_public
        }

class UserSubscription(db.Model):
    """User subscription model"""
    __tablename__ = 'user_subscription'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('billing_plan.id'), nullable=False)
    
    # Subscription details
    status = db.Column(db.String(20), default='active')  # active, cancelled, expired, pending
    current_period_start = db.Column(db.DateTime, nullable=False)
    current_period_end = db.Column(db.DateTime, nullable=False)
    
    # Token tracking
    tokens_used_this_period = db.Column(db.Integer, default=0)
    tokens_purchased_this_period = db.Column(db.Integer, default=0)
    
    # Payment integration
    stripe_subscription_id = db.Column(db.String(100))
    stripe_customer_id = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert subscription to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'status': self.status,
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'tokens_used_this_period': self.tokens_used_this_period,
            'tokens_purchased_this_period': self.tokens_purchased_this_period,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ProjectCollaborator(db.Model):
    """Project collaboration model"""
    __tablename__ = 'project_collaborator'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Collaboration details
    role = db.Column(db.String(20), default='editor')  # owner, editor, viewer, commenter
    permissions = db.Column(db.JSON)  # Specific permissions
    status = db.Column(db.String(20), default='active')  # active, invited, removed
    
    # Invitation details
    invitation_token = db.Column(db.String(100))
    invited_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    invited_at = db.Column(db.DateTime)
    joined_at = db.Column(db.DateTime)
    last_access = db.Column(db.DateTime)
    
    def to_dict(self):
        """Convert collaborator to dictionary"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'role': self.role,
            'permissions': self.permissions,
            'status': self.status,
            'invited_at': self.invited_at.isoformat() if self.invited_at else None,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'last_access': self.last_access.isoformat() if self.last_access else None
        }

class Comment(db.Model):
    """Comments model for collaboration"""
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    
    # Target (what is being commented on)
    target_type = db.Column(db.String(20), nullable=False)  # project, scene, story_object
    target_id = db.Column(db.String(100), nullable=False)  # ID of the target
    
    # Comment thread
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    thread_position = db.Column(db.Integer, default=0)  # Position in thread
    
    # Status
    is_resolved = db.Column(db.Boolean, default=False)
    is_edited = db.Column(db.Boolean, default=False)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    scene_id = db.Column(db.Integer, db.ForeignKey('scene.id'))  # Optional: if commenting on scene
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def to_dict(self, include_replies=False):
        """Convert comment to dictionary"""
        data = {
            'id': self.id,
            'content': self.content,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'parent_comment_id': self.parent_comment_id,
            'thread_position': self.thread_position,
            'is_resolved': self.is_resolved,
            'is_edited': self.is_edited,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'scene_id': self.scene_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_replies:
            data['replies'] = [reply.to_dict() for reply in self.replies.all()]
        
        return data