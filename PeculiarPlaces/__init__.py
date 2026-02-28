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

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    cache.init_app(app)

    from . import api
    from . import models
    app.cli.add_command(models.init_db_command)
    app.register_blueprint(api.api_bp)

    return app