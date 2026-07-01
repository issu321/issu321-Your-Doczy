from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"


def create_app(config_class=Config):
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )

    app.config.from_object(config_class)

    # Create upload directories if they don't exist
    upload_folder = app.config.get("UPLOAD_FOLDER")
    converted_folder = app.config.get("CONVERTED_FOLDER")

    if upload_folder:
        upload_folder.mkdir(parents=True, exist_ok=True)

    if converted_folder:
        converted_folder.mkdir(parents=True, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.converter import bp as converter_bp
    app.register_blueprint(converter_bp, url_prefix="/convert")

    return app


from app import models
