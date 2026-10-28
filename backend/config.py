import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-dev-key-change-in-prod-2026'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-dev-key-ai-predictor-2026'
    JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 24))
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or f"sqlite:///{os.path.join(basedir, 'data', 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads & Artifacts
    UPLOAD_FOLDER = os.path.join(basedir, 'data', 'uploads')
    DATA_FOLDER = os.path.join(basedir, 'data')
    ARTIFACTS_FOLDER = os.path.join(basedir, 'artifacts')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'csv'}

    # Shadow Mode & Telemetry Feature Flags (Disabled by default)
    SHADOW_MODE_ENABLED = os.environ.get('SHADOW_MODE_ENABLED', 'false').lower() == 'true'
    SHADOW_CANDIDATE_VERSION = os.environ.get('SHADOW_CANDIDATE_VERSION', 'lms_canonical_v1')

    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

