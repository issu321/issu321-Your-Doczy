import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'doczy-super-secret-key-2026-change-me'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///doczy.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_DIR = Path(__file__).parent
    UPLOAD_FOLDER = BASE_DIR / 'app' / 'static' / 'uploads'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload
    CONVERTED_FOLDER = BASE_DIR / 'app' / 'static' / 'uploads' / 'converted'
