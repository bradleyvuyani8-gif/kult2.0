import os

class Config:
    """Core configuration class for KULT e-commerce application."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kult-secret-key-change-in-production-secure-key'
    
    # Direct persistent storage path pointing to your shared Android KULTDATABASE folder
    DATABASE_PATH = '/storage/emulated/0/KULTDATABASE/store.db'
    
    # Application runtime configuration
    DEBUG = True
    TESTING = False
    
    # Security and session configurations
    SESSION_COOKIE_SECURE = False  # Set to True if running under HTTPS in production
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 86400  # 1 day in seconds
