# app/models.py - ALVIN Database Models
"""
Simple models file that avoids circular imports
"""
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(500))
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Subscription info
    plan = db.Column(db.String(50), default='free')
    tokens_used = db.Column(db.Integer, default=0)
    tokens_limit = db.Column(db.Integer, default=1000)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    projects = db.relationship('Project', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_remaining_tokens(self):
        """Get remaining token count"""
        return max(0, self.tokens_limit - self.tokens_used)
    
    def can_afford_tokens(self, token_cost):
        """Check if user can afford token cost"""
        return self.get_remaining_tokens() >= token_cost
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
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
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Project(db.Model):
    """Project model for story projects"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Project metadata
    genre = db.Column(db.String(100))
    target_audience = db.Column(db.String(100))
    expected_length = db.Column(db.String(50))  # short, medium, long
    status = db.Column(db.String(50), default='active')  # active, completed, archived
    
    # Writing progress
    current_word_count = db.Column(db.Integer, default=0)
    target_word_count = db.Column(db.Integer)
    
    # User relationship
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ADD these missing fields that analytics.py expects:
    current_phase = db.Column(db.String(50), default='idea')  # idea, expand, story
    tone = db.Column(db.String(100))
    estimated_scope = db.Column(db.String(50))
    marketability = db.Column(db.Integer)  # 1-5 rating
    original_idea = db.Column(db.Text)  # Store the original idea text
    
    # Relationships
    scenes = db.relationship('Scene', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    story_objects = db.relationship('StoryObject', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'genre': self.genre,
            'target_audience': self.target_audience,
            'expected_length': self.expected_length,
            'status': self.status,
            'current_word_count': self.current_word_count,
            'target_word_count': self.target_word_count,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'scene_count': self.scenes.count(),
            'object_count': self.story_objects.count()
        }

class Scene(db.Model):
    """Scene model for individual scenes within projects"""
    __tablename__ = 'scenes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    
    # Scene metadata
    scene_type = db.Column(db.String(50), default='development')  # opening, inciting, development, climax, resolution
    emotional_intensity = db.Column(db.Float, default=0.5)  # 0.0 to 1.0
    order_index = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='draft')  # draft, completed, needs_review
    
    # Word count
    word_count = db.Column(db.Integer, default=0)
    
    # Project relationship
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'scene_type': self.scene_type,
            'emotional_intensity': self.emotional_intensity,
            'order_index': self.order_index,
            'status': self.status,
            'word_count': self.word_count,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class StoryObject(db.Model):
    """Story objects like characters, locations, items"""
    __tablename__ = 'story_objects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    object_type = db.Column(db.String(50), nullable=False)  # character, location, item, concept
    description = db.Column(db.Text)
    
    # Object details stored as JSON
    attributes = db.Column(db.JSON)  # Flexible storage for object-specific data
    
    # Project relationship
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'object_type': self.object_type,
            'description': self.description,
            'attributes': self.attributes,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BillingPlan(db.Model):
    """Billing plans for subscription management"""
    __tablename__ = 'billing_plans'  # Make sure this matches the foreign key reference
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Pricing
    price_monthly = db.Column(db.Numeric(10, 2))
    price_yearly = db.Column(db.Numeric(10, 2))
    
    # Limits
    token_limit = db.Column(db.Integer, nullable=False)
    project_limit = db.Column(db.Integer)
    
    # Features
    features = db.Column(db.JSON)  # List of features
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'price_monthly': float(self.price_monthly) if self.price_monthly else None,
            'price_yearly': float(self.price_yearly) if self.price_yearly else None,
            'token_limit': self.token_limit,
            'project_limit': self.project_limit,
            'features': self.features,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class TokenUsageLog(db.Model):
    """Token usage tracking for billing"""
    __tablename__ = 'token_usage_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    operation_type = db.Column(db.String(50), nullable=False)  # analyze_idea, create_project, etc.
    
    # Token counts
    input_tokens = db.Column(db.Integer, default=0)
    output_tokens = db.Column(db.Integer, default=0)
    total_cost = db.Column(db.Integer, default=0)  # Total tokens charged to user
    
    # Metadata
    model_used = db.Column(db.String(100))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    
    # Billing
    billable = db.Column(db.Boolean, default=True)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='token_usage')
    project = db.relationship('Project', backref='token_usage')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'operation_type': self.operation_type,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_cost': self.total_cost,
            'model_used': self.model_used,
            'project_id': self.project_id,
            'billable': self.billable,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
class SceneObject(db.Model):
    """Many-to-many relationship between scenes and story objects"""
    __tablename__ = 'scene_objects'
    
    id = db.Column(db.Integer, primary_key=True)
    scene_id = db.Column(db.Integer, db.ForeignKey('scene.id'), nullable=False)
    object_id = db.Column(db.Integer, db.ForeignKey('story_object.id'), nullable=False)
    
    # Role of object in this scene
    role = db.Column(db.String(100))  # 'protagonist', 'antagonist', 'background', etc.
    importance_in_scene = db.Column(db.String(20), default='medium')  # low, medium, high
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'scene_id': self.scene_id,
            'object_id': self.object_id,
            'role': self.role,
            'importance_in_scene': self.importance_in_scene,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Comment(db.Model):
    """Comments and feedback system"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    
    # What this comment is attached to
    target_type = db.Column(db.String(50), nullable=False)  # 'project', 'scene', 'story_object'
    target_id = db.Column(db.String(50), nullable=False)
    
    # Author
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Threading support
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    
    # Status
    is_resolved = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', backref='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'content': self.content,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'user_id': self.user_id,
            'parent_comment_id': self.parent_comment_id,
            'is_resolved': self.is_resolved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'author': self.author.username if self.author else None,
            'reply_count': len(self.replies) if self.replies else 0
        }


class ProjectCollaborator(db.Model):
    """Project collaboration and team management"""
    __tablename__ = 'project_collaborators'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Role and permissions
    role = db.Column(db.String(50), default='editor')  # owner, editor, viewer, commenter
    permissions = db.Column(db.JSON)  # Custom permissions object
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, inactive, pending
    
    # Invitation details
    invited_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    invited_at = db.Column(db.DateTime, default=datetime.utcnow)
    joined_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref='collaborators')
    user = db.relationship('User', foreign_keys=[user_id], backref='collaborations')
    inviter = db.relationship('User', foreign_keys=[invited_by])
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'role': self.role,
            'permissions': self.permissions,
            'status': self.status,
            'invited_by': self.invited_by,
            'invited_at': self.invited_at.isoformat() if self.invited_at else None,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user': self.user.username if self.user else None,
            'project': self.project.title if self.project else None
        }
    
class UserSubscription(db.Model):
    """User subscription model for billing"""
    __tablename__ = 'user_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('billing_plans.id'), nullable=False)
    
    # Subscription status
    status = db.Column(db.String(20), default='active', index=True)  # active, cancelled, expired
    
    # Billing period
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    
    # Stripe integration (for future use)
    stripe_subscription_id = db.Column(db.String(100), unique=True)
    stripe_customer_id = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='subscriptions')
    plan = db.relationship('BillingPlan', backref='subscriptions')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'status': self.status,
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'stripe_subscription_id': self.stripe_subscription_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Export all models
__all__ = [
    'User',
    'Project', 
    'Scene', 
    'StoryObject',
    'BillingPlan',
    'TokenUsageLog',
    'SceneObject',
    'Comment',
    'UserSubscription'
    'ProjectCollaborator'
]