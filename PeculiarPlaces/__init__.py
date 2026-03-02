import os
#from flasgger import Swagger
from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
cache = Cache()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(app.instance_path, "development.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CACHE_TYPE'] = 'FileSystemCache'
    app.config['CACHE_DIR'] = os.path.join(app.instance_path, 'cache')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    cache.init_app(app)

    # Register converter BEFORE blueprint
    from .utils import PlaceConverter, ImageConverter
    app.url_map.converters['place'] = PlaceConverter
    app.url_map.converters["image"] = ImageConverter

    from .api import api_bp
    from . import models
    app.cli.add_command(models.init_db_command)
    app.register_blueprint(api_bp)

    return app