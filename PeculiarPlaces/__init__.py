import os
from pathlib import Path

from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

db = SQLAlchemy()
cache = Cache()


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        app.instance_path, "development.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["CACHE_TYPE"] = "FileSystemCache"
    app.config["CACHE_DIR"] = os.path.join(app.instance_path, "cache")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "development_secret_key")
    app.config["UPLOAD_FOLDER"] = os.path.join(app.instance_path, "uploads")
    app.config["SWAGGER"] = {
        "title": "PeculiarPlaces API",
        "openapi": "3.0.0",
        "uiversion": 3,
    }
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    cache.init_app(app)
    from .utils import ImageConverter, PlaceConverter

    app.url_map.converters["place"] = PlaceConverter
    app.url_map.converters["image"] = ImageConverter

    from . import models
    from .api import api_bp

    app.cli.add_command(models.init_db_command)
    app.register_blueprint(api_bp)

    swagger = Swagger(app, template_file="doc/openapi.yml")
    
    return app
