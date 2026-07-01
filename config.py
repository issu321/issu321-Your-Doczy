import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    # Security
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "doczy-super-secret-key-2026-change-me"
    )

    # Database
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        # Render PostgreSQL compatibility
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL or f"sqlite:///{BASE_DIR / 'doczy.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folders
    UPLOAD_FOLDER = BASE_DIR / "app" / "static" / "uploads"
    CONVERTED_FOLDER = UPLOAD_FOLDER / "converted"

    # Maximum upload size (50 MB)
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
