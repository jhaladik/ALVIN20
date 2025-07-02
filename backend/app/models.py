# app/models.py - CORRECTED TABLE NAMES TO MATCH MIGRATIONS
"""
Database models with corrected table names that match migrations
"""
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'user'  # FIXED: Changed from 'users' to 'user'
    
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
    
    # Relationships - FIXED foreign key references
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
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'plan': self.plan,
            'tokens_used': self.tokens_used,
            'tokens_limit': self.tokens_limit,
            'remaining_tokens': self.get_remaining_tokens(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Project(db.Model):
    """Project model for story projects"""
    __tablename__ = 'project'  # FIXED: Changed from 'projects' to 'project'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Story metadata
    genre = db.Column(db.String(100))
    target_audience = db.Column(db.String(100))
    expected_length = db.Column(db.String(50))  # 'short', 'medium', 'novel'
    
    # Project status
    status = db.Column(db.String(50), default='active')  # active, paused, completed, archived
    current_phase = db.Column(db.String(50), default='idea')  # idea, expand, story
    
    # Word count tracking
    current_word_count = db.Column(db.Integer, default=0)
    target_word_count = db.Column(db.Integer)
    
    # AI analysis results (stored as JSON)
    analysis_results = db.Column(db.JSON)
    original_idea = db.Column(db.Text)
    
    # Additional metadata
    tone = db.Column(db.String(100))
    estimated_scope = db.Column(db.String(100))
    marketability = db.Column(db.Integer)  # 1-5 scale
    
    # Foreign key - FIXED reference
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - FIXED foreign key references
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
            'current_phase': self.current_phase,
            'current_word_count': self.current_word_count,
            'target_word_count': self.target_word_count,
            'tone': self.tone,
            'estimated_scope': self.estimated_scope,
            'marketability': self.marketability,
            'original_idea': self.original_idea,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'scene_count': self.scenes.count(),
            'object_count': self.story_objects.count()
        }

class Scene(db.Model):
    """Scene model for individual scenes within projects"""
    __tablename__ = 'scene'  # FIXED: Changed from 'scenes' to 'scene'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    
    # Scene metadata
    scene_type = db.Column(db.String(50), default='development')  # opening, inciting, development, climax, resolution
    emotional_intensity = db.Column(db.Float, default=0.5)  # 0.0 to 1.0
    order_index = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='draft')  # draft, completed, needs_review
    
    # Additional scene details
    location = db.Column(db.String(200))
    conflict = db.Column(db.Text)
    hook = db.Column(db.Text)
    character_focus = db.Column(db.String(200))
    
    # Word count tracking
    word_count = db.Column(db.Integer, default=0)
    dialog_count = db.Column(db.Integer, default=0)
    
    # Foreign key - FIXED reference
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    
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
            'location': self.location,
            'conflict': self.conflict,
            'hook': self.hook,
            'character_focus': self.character_focus,
            'word_count': self.word_count,
            'dialog_count': self.dialog_count,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class StoryObject(db.Model):
    """Story objects like characters, locations, items"""
    __tablename__ = 'story_object'  # FIXED: Changed from 'story_objects' to 'story_object'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    object_type = db.Column(db.String(50), nullable=False)  # character, location, object, concept
    description = db.Column(db.Text)
    
    # Story object details
    importance = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(20), default='active')  # active, inactive, removed
    
    # Character-specific fields
    character_role = db.Column(db.String(50))  # protagonist, antagonist, supporting, etc.
    
    # Symbolic meaning and themes
    symbolic_meaning = db.Column(db.Text)
    
    # Object details stored as JSON for flexibility
    attributes = db.Column(db.JSON)
    
    # Foreign key - FIXED reference
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    
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
            'importance': self.importance,
            'status': self.status,
            'character_role': self.character_role,
            'symbolic_meaning': self.symbolic_meaning,
            'attributes': self.attributes,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SceneObject(db.Model):
    """Many-to-many relationship between scenes and story objects"""
    __tablename__ = 'scene_object'  # FIXED: Changed from 'scene_objects' to 'scene_object'
    
    id = db.Column(db.Integer, primary_key=True)
    scene_id = db.Column(db.Integer, db.ForeignKey('scene.id'), nullable=False)
    object_id = db.Column(db.Integer, db.ForeignKey('story_object.id'), nullable=False)
    
    # Role and interaction details
    role = db.Column(db.String(100))  # 'protagonist', 'antagonist', 'background', etc.
    transformation = db.Column(db.Text)  # How the object changes in this scene
    significance = db.Column(db.String(20), default='medium')  # low, medium, high
    interaction_type = db.Column(db.String(50))  # dialogue, action, mention, etc.
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'scene_id': self.scene_id,
            'object_id': self.object_id,
            'role': self.role,
            'transformation': self.transformation,
            'significance': self.significance,
            'interaction_type': self.interaction_type
        }

# Additional models for token tracking and billing
class TokenUsageLog(db.Model):
    """Track token usage for billing and analytics"""
    __tablename__ = 'token_usage_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    operation_type = db.Column(db.String(100), nullable=False)
    
    # Token counts
    input_tokens = db.Column(db.Integer, default=0)
    output_tokens = db.Column(db.Integer, default=0)
    total_cost = db.Column(db.Integer, default=0)  # Total tokens charged to user
    
    # Metadata
    model_used = db.Column(db.String(100))
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'))
    scene_id = db.Column(db.Integer, db.ForeignKey('scene.id'))
    
    # Billing
    billable = db.Column(db.Boolean, default=True)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships - FIXED foreign key references
    user = db.relationship('User', backref='token_usage')
    project = db.relationship('Project', backref='token_usage')
    scene = db.relationship('Scene', backref='token_usage')
    
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
            'scene_id': self.scene_id,
            'billable': self.billable,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BillingPlan(db.Model):
    """Billing plans for subscriptions"""
    __tablename__ = 'billing_plan'
    
    id = db.Column(db.String(50), primary_key=True)  # 'free', 'pro', 'enterprise'
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price_monthly = db.Column(db.Integer, default=0)  # Price in cents
    price_yearly = db.Column(db.Integer, default=0)   # Price in cents
    token_limit = db.Column(db.Integer, default=1000)
    max_projects = db.Column(db.Integer, default=5)
    max_scenes_per_project = db.Column(db.Integer, default=50)
    features = db.Column(db.JSON)  # JSON array of feature strings
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price_monthly': self.price_monthly,
            'price_yearly': self.price_yearly,
            'token_limit': self.token_limit,
            'max_projects': self.max_projects,
            'max_scenes_per_project': self.max_scenes_per_project,
            'features': self.features,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserSubscription(db.Model):
    """User subscription tracking"""
    __tablename__ = 'user_subscription'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    plan_id = db.Column(db.String(50), db.ForeignKey('billing_plan.id'), nullable=False)
    
    # Subscription status
    status = db.Column(db.String(50), default='active')  # active, cancelled, expired, trial
    
    # Billing details
    stripe_subscription_id = db.Column(db.String(100))
    stripe_customer_id = db.Column(db.String(100))
    
    # Trial information
    trial_start = db.Column(db.DateTime)
    trial_end = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - FIXED foreign key references
    user = db.relationship('User', backref='subscription')
    plan = db.relationship('BillingPlan', backref='subscriptions')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'status': self.status,
            'stripe_subscription_id': self.stripe_subscription_id,
            'stripe_customer_id': self.stripe_customer_id,
            'trial_start': self.trial_start.isoformat() if self.trial_start else None,
            'trial_end': self.trial_end.isoformat() if self.trial_end else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
class Comment(db.Model):
    """Comments for project collaboration and feedback"""
    __tablename__ = 'comment'  # Match migration table name
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    
    # Target of comment (project, scene, or story object)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    scene_id = db.Column(db.Integer, db.ForeignKey('scene.id'), nullable=True)
    
    # Comment authorship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Thread support
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    thread_depth = db.Column(db.Integer, default=0)
    
    # Comment status
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Comment metadata
    comment_type = db.Column(db.String(20), default='general')  # general, suggestion, issue, approval
    position_data = db.Column(db.JSON)  # For positioning comments on specific text/elements
    is_edited = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - FIXED to match corrected table names
    project = db.relationship('Project', backref='comments')
    scene = db.relationship('Scene', backref='comments')
    author = db.relationship('User', foreign_keys=[user_id], backref='comments')
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='resolved_comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'content': self.content,
            'project_id': self.project_id,
            'scene_id': self.scene_id,
            'user_id': self.user_id,
            'parent_comment_id': self.parent_comment_id,
            'thread_depth': self.thread_depth,
            'is_resolved': self.is_resolved,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'comment_type': self.comment_type,
            'position_data': self.position_data,
            'is_edited': self.is_edited,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'author': self.author.username if self.author else None,
            'reply_count': len(self.replies) if self.replies else 0
        }

class ProjectCollaborator(db.Model):
    """Project collaboration and team management"""
    __tablename__ = 'project_collaborator'  # Match migration table name
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Role and permissions
    role = db.Column(db.String(50), default='editor')  # owner, editor, viewer, commenter
    permissions = db.Column(db.JSON)  # Custom permissions object
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, inactive, pending
    
    # Invitation details
    invited_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    invited_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - FIXED to match corrected table names
    project = db.relationship('Project', backref='collaborators')
    user = db.relationship('User', foreign_keys=[user_id], backref='collaborations')
    inviter = db.relationship('User', foreign_keys=[invited_by], backref='sent_invitations')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('project_id', 'user_id', name='unique_project_user'),)
    
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
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
                'full_name': self.user.full_name
            } if self.user else None,
            'inviter': {
                'id': self.inviter.id,
                'username': self.inviter.username
            } if self.inviter else None
        }

# UPDATE: Add these to the __all__ export list at the bottom of models.py
__all__ = [
    'User',
    'Project', 
    'Scene', 
    'StoryObject',
    'SceneObject',
    'TokenUsageLog',
    'BillingPlan',
    'UserSubscription',
    'Comment',           # ADD THIS
    'ProjectCollaborator' # ADD THIS
]