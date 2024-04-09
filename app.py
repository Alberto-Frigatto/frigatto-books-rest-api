from flask import Flask, request
from flask_cors import CORS
from sqlalchemy import text

from api import api
from db import db
from handle_errors import import_error_messages
from json_web_token import jwt
from response import ResponseError
from routes import add_routes
from schemas import ma

app = Flask(__name__)
app.config.from_pyfile('./config.py')

CORS(app)

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
        return ResponseError(api.errors.get('DatabaseConnection')).json()


@app.before_request
def check_http_method():
    method = request.method
    route = request.path

    adapter = app.url_map.bind('')
    try:
        adapter.match(route, method)
    except Exception:
        return ResponseError(api.errors.get('MethodNotAllowed')).json()


@app.before_request
def check_content_type_for_contents_sent():
    allowed_content_type = 'application/json'

    if request.content_length and request.content_type != allowed_content_type:
        return ResponseError(api.errors.get('InvalidContentType')).json()


add_routes(app)
