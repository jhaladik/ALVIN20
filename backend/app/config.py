#!/usr/bin/env python3
"""
config.py - ALVIN Backend Configuration
Place this file in backend/config.py (not in the app folder)
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
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}
    
    # Email Configuration (for notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Redis Configuration (for caching and sessions)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # CORS Settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    
    # Socket.IO Configuration
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_CORS_ALLOWED_ORIGINS = CORS_ORIGINS
    
    # Pagination
    PROJECTS_PER_PAGE = 20
    SCENES_PER_PAGE = 50
    COMMENTS_PER_PAGE = 30
    
    # Export Settings
    EXPORT_TIMEOUT = 60  # seconds
    MAX_EXPORT_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Stripe Configuration (for billing)
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Payment Simulation (for development)
    PAYMENT_SIMULATION_MODE = os.environ.get('PAYMENT_SIMULATION_MODE', 'true').lower() == 'true'
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE')  # If None, logs to console

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Use SQLite for development if no DATABASE_URL provided
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///alvin_dev.db'
    
    # More lenient rate limiting for development
    CLAUDE_MAX_REQUESTS_PER_MINUTE = 100
    
    # Enable AI simulation mode by default in development
    AI_SIMULATION_MODE = os.environ.get('AI_SIMULATION_MODE', 'true').lower() == 'true'
    
    # Enable payment simulation mode in development
    PAYMENT_SIMULATION_MODE = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Force simulation modes for testing
    AI_SIMULATION_MODE = True
    PAYMENT_SIMULATION_MODE = True
    
    # Faster token expiration for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=1)

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Require real database URL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        print("Warning: DATABASE_URL not set, using SQLite")
        SQLALCHEMY_DATABASE_URI = 'sqlite:///alvin_prod.db'
    
    # Stricter rate limiting in production
    CLAUDE_MAX_REQUESTS_PER_MINUTE = 50

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class by name"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    return config.get(config_name, DevelopmentConfig)