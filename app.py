from flask import Flask, request
from flask_cors import CORS
from sqlalchemy import text

from api import api
from db import db
from handle_errors import CustomError, import_error_messages
from json_web_token import jwt
from response import ResponseError
from routes import add_routes
from schemas import ma


def create_app(test_config: bool = False) -> Flask:
    app = Flask(__name__)

    if test_config:
        app.config.from_mapping(
            SECRET_KEY='key',
            SQLALCHEMY_DATABASE_URI='sqlite:///',
            JWT_SECRET_KEY='key',
            JWT_TOKEN_LOCATION=['headers'],
            JWT_HEADER_TYPE='Bearer',
            JWT_SESSION_COOKIE=False,
            JWT_ACCESS_TOKEN_EXPIRES=False,
            JWT_COOKIE_SECURE=True,
            JWT_COOKIE_SAMESITE="Strict",
            RESPONSE_HEADERS=[
                ('Content-Type', 'application/json;charset=utf-8'),
                ('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-CSRF-TOKEN'),
                ('Access-Control-Allow-Credentials', 'true'),
            ],
            TESTING=True,
            USER_PHOTOS_UPLOAD_DIR='tests/uploads',
            USER_PHOTOS_MAX_SIZE=5 * 1024 * 1024,
            BOOK_PHOTOS_UPLOAD_DIR='tests/uploads',
            BOOK_PHOTOS_MAX_SIZE=7 * 1024 * 1024,
        )
    else:
        app.config.from_pyfile('./config.py')

    CORS(app, supports_credentials=True)

    jwt.init_app(app)
    api.init_app(app)
    db.init_app(app)
    ma.init_app(app)

    import_error_messages(api)

    @app.before_request
    def check_db_connection():
        try:
            db.session.execute(text('SELECT 1'))
            db.session.commit()
        except Exception:
            return ResponseError(CustomError('DatabaseConnection')).json()

    @app.before_request
    def check_http_method():
        method = request.method
        route = request.path

        adapter = app.url_map.bind('')
        try:
            adapter.match(route, method)
        except Exception:
            return ResponseError(CustomError('MethodNotAllowed')).json()

    @app.before_request
    def check_content_type():
        allowed_content_types = 'multipart/form-data', 'application/json'

        if request.content_length and all(
            allowed_content_type not in request.content_type
            for allowed_content_type in allowed_content_types
        ):
            return ResponseError(CustomError('InvalidContentType')).json()

    add_routes(app)

    return app
