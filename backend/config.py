# config.py - COMPLETE CONFIGURATION WITH ALL MISSING VALUES
"""
Complete configuration file that includes all values referenced by routes
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Core Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'alvin-dev-secret-key-change-in-production'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///alvin.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # Claude API Configuration
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    AI_SIMULATION_MODE = os.environ.get('AI_SIMULATION_MODE', 'true').lower() == 'true'
    DEFAULT_CLAUDE_MODEL = os.environ.get('DEFAULT_CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
    
    # Rate Limiting for Claude API
    CLAUDE_MAX_REQUESTS_PER_MINUTE = int(os.environ.get('CLAUDE_MAX_REQUESTS_PER_MINUTE', 50))
    CLAUDE_MAX_TOKENS_PER_REQUEST = int(os.environ.get('CLAUDE_MAX_TOKENS_PER_REQUEST', 4000))
    
    # Token Limits by Plan
    TOKEN_LIMITS = {
        'free': 1000,
        'pro': 10000,
        'enterprise': 50000
    }
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'rtf'}
    
    # PAGINATION SETTINGS - MISSING VALUES THAT ROUTES EXPECT
    PROJECTS_PER_PAGE = int(os.environ.get('PROJECTS_PER_PAGE', 20))
    SCENES_PER_PAGE = int(os.environ.get('SCENES_PER_PAGE', 50))
    OBJECTS_PER_PAGE = int(os.environ.get('OBJECTS_PER_PAGE', 100))
    ANALYTICS_ITEMS_PER_PAGE = int(os.environ.get('ANALYTICS_ITEMS_PER_PAGE', 50))
    
    # ACTIVITY LOGGING
    MAX_RECENT_ACTIVITIES = int(os.environ.get('MAX_RECENT_ACTIVITIES', 100))
    ACTIVITY_RETENTION_DAYS = int(os.environ.get('ACTIVITY_RETENTION_DAYS', 30))
    
    # PROJECT LIMITS
    MAX_PROJECTS_FREE = int(os.environ.get('MAX_PROJECTS_FREE', 3))
    MAX_PROJECTS_PRO = int(os.environ.get('MAX_PROJECTS_PRO', 25))
    MAX_PROJECTS_ENTERPRISE = int(os.environ.get('MAX_PROJECTS_ENTERPRISE', 100))
    
    # SCENE LIMITS
    MAX_SCENES_PER_PROJECT_FREE = int(os.environ.get('MAX_SCENES_PER_PROJECT_FREE', 20))
    MAX_SCENES_PER_PROJECT_PRO = int(os.environ.get('MAX_SCENES_PER_PROJECT_PRO', 100))
    MAX_SCENES_PER_PROJECT_ENTERPRISE = int(os.environ.get('MAX_SCENES_PER_PROJECT_ENTERPRISE', 500))
    
    # OBJECT LIMITS
    MAX_OBJECTS_PER_PROJECT_FREE = int(os.environ.get('MAX_OBJECTS_PER_PROJECT_FREE', 50))
    MAX_OBJECTS_PER_PROJECT_PRO = int(os.environ.get('MAX_OBJECTS_PER_PROJECT_PRO', 200))
    MAX_OBJECTS_PER_PROJECT_ENTERPRISE = int(os.environ.get('MAX_OBJECTS_PER_PROJECT_ENTERPRISE', 1000))
    
    # EMAIL CONFIGURATION
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME
    
    # STRIPE BILLING CONFIGURATION
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    PAYMENT_SIMULATION_MODE = os.environ.get('PAYMENT_SIMULATION_MODE', 'true').lower() == 'true'
    
    # REDIS CONFIGURATION (for caching and sessions)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    # CORS CONFIGURATION
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    
    # LOGGING CONFIGURATION
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # SECURITY SETTINGS
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # AI OPERATION TIMEOUTS
    AI_OPERATION_TIMEOUT = int(os.environ.get('AI_OPERATION_TIMEOUT', 120))  # seconds
    MAX_CONCURRENT_AI_OPERATIONS = int(os.environ.get('MAX_CONCURRENT_AI_OPERATIONS', 5))
    
    # EXPORT SETTINGS
    EXPORT_MAX_FILE_SIZE = int(os.environ.get('EXPORT_MAX_FILE_SIZE', 50 * 1024 * 1024))  # 50MB
    EXPORT_SUPPORTED_FORMATS = ['txt', 'html', 'pdf', 'docx', 'json']
    
    # COLLABORATION SETTINGS
    MAX_COLLABORATORS_PER_PROJECT = int(os.environ.get('MAX_COLLABORATORS_PER_PROJECT', 10))
    COLLABORATION_REALTIME_ENABLED = os.environ.get('COLLABORATION_REALTIME_ENABLED', 'true').lower() == 'true'
    
    # ANALYTICS SETTINGS
    ANALYTICS_ENABLED = os.environ.get('ANALYTICS_ENABLED', 'true').lower() == 'true'
    ANALYTICS_DATA_RETENTION_DAYS = int(os.environ.get('ANALYTICS_DATA_RETENTION_DAYS', 90))
    
    # RATE LIMITING
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # API RATE LIMITS BY ENDPOINT
    RATE_LIMITS = {
        'auth': '10 per minute',
        'projects': '60 per minute', 
        'scenes': '100 per minute',
        'objects': '100 per minute',
        'ai': '10 per minute',
        'analytics': '30 per minute',
        'collaboration': '120 per minute',
        'billing': '20 per minute'
    }
    
    # PLAN CONFIGURATIONS
    PLAN_CONFIGS = {
        'free': {
            'max_projects': MAX_PROJECTS_FREE,
            'max_scenes_per_project': MAX_SCENES_PER_PROJECT_FREE,
            'max_objects_per_project': MAX_OBJECTS_PER_PROJECT_FREE,
            'max_collaborators': 1,
            'token_limit': TOKEN_LIMITS['free'],
            'ai_operations_per_day': 10,
            'export_formats': ['txt', 'html'],
            'analytics_enabled': False,
            'priority_support': False
        },
        'pro': {
            'max_projects': MAX_PROJECTS_PRO,
            'max_scenes_per_project': MAX_SCENES_PER_PROJECT_PRO,
            'max_objects_per_project': MAX_OBJECTS_PER_PROJECT_PRO,
            'max_collaborators': 5,
            'token_limit': TOKEN_LIMITS['pro'],
            'ai_operations_per_day': 100,
            'export_formats': ['txt', 'html', 'pdf', 'docx'],
            'analytics_enabled': True,
            'priority_support': True
        },
        'enterprise': {
            'max_projects': MAX_PROJECTS_ENTERPRISE,
            'max_scenes_per_project': MAX_SCENES_PER_PROJECT_ENTERPRISE,
            'max_objects_per_project': MAX_OBJECTS_PER_PROJECT_ENTERPRISE,
            'max_collaborators': MAX_COLLABORATORS_PER_PROJECT,
            'token_limit': TOKEN_LIMITS['enterprise'],
            'ai_operations_per_day': 1000,
            'export_formats': EXPORT_SUPPORTED_FORMATS,
            'analytics_enabled': True,
            'priority_support': True,
            'custom_integrations': True
        }
    }
    
    # BACKUP AND RECOVERY
    AUTO_BACKUP_ENABLED = os.environ.get('AUTO_BACKUP_ENABLED', 'false').lower() == 'true'
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', 30))
    
    # MONITORING AND HEALTH CHECKS
    HEALTH_CHECK_TIMEOUT = int(os.environ.get('HEALTH_CHECK_TIMEOUT', 5))
    METRICS_ENABLED = os.environ.get('METRICS_ENABLED', 'true').lower() == 'true'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Override for development
    AI_SIMULATION_MODE = True
    PAYMENT_SIMULATION_MODE = True
    LOG_LEVEL = 'DEBUG'
    
    # Development database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///alvin_dev.db'
    
    # Relaxed rate limiting for development
    RATE_LIMITS = {
        'auth': '100 per minute',
        'projects': '300 per minute', 
        'scenes': '500 per minute',
        'objects': '500 per minute',
        'ai': '50 per minute',
        'analytics': '100 per minute',
        'collaboration': '600 per minute',
        'billing': '100 per minute'
    }

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Stricter settings for production
    AI_SIMULATION_MODE = False
    PAYMENT_SIMULATION_MODE = False
    
    # Production database (required)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable required for production")
    
    # Required API keys for production
    if not Config.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable required for production")
    
    if not Config.STRIPE_SECRET_KEY:
        raise ValueError("STRIPE_SECRET_KEY environment variable required for production")

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    
    # Test database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Test mode settings
    AI_SIMULATION_MODE = True
    PAYMENT_SIMULATION_MODE = True
    
    # Faster token expiration for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    
    # Unlimited rate limits for testing
    RATE_LIMITS = {}

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}