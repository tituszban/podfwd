import os
import sys
from flask import Flask
from flask_cors import CORS

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dev_api.routes import emails_bp, parse_bp, audio_bp
from dev_api.dependencies import get_dependencies, DevConfig


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Initialize dependencies
    deps = get_dependencies()
    dev_config = deps.get(DevConfig)

    # Store dependencies on app for access in routes
    app.deps = deps

    # Configure paths (for backwards compatibility)
    app.config["SOURCES_FOLDER"] = dev_config.sources_folder
    app.config["DEV_DATA_FOLDER"] = dev_config.dev_data_folder
    app.config["AUDIO_CACHE_FOLDER"] = dev_config.audio_cache_folder

    # Register blueprints
    app.register_blueprint(emails_bp, url_prefix="/api/emails")
    app.register_blueprint(parse_bp, url_prefix="/api/parse")
    app.register_blueprint(audio_bp, url_prefix="/api/audio")

    return app
