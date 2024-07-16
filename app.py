from flask import Flask
from flask_cors import CORS
from flask_injector import FlaskInjector

from config import (
    add_error_handlers,
    add_middlewares,
    add_routes,
    create_upload_dirs_if_dont_exist,
    di_config,
)
from db import db
from security import jwt


def create_app(test_config: bool = False) -> Flask:
    app = Flask(__name__)

    app.config.from_pyfile('./config/app_general.py')
    app.config.from_pyfile(f'./config/{"app_dev" if test_config else "app_production"}.py')

    CORS(app, supports_credentials=True)

    jwt.init_app(app)
    db.init_app(app)

    add_middlewares(app)
    add_error_handlers(app)
    add_routes(app)

    create_upload_dirs_if_dont_exist(app)

    FlaskInjector(app=app, modules=[di_config])

    return app
