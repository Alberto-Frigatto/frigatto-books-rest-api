from flask import Flask, Response, request
from sqlalchemy import text
from werkzeug.exceptions import MethodNotAllowed, NotFound

from db import db
from exception import GeneralException
from response import ResponseError, ResponseSuccess


def add_middlewares(app: Flask) -> None:
    @app.before_request
    def check_db_connection() -> Response | None:
        try:
            db.session.execute(text('SELECT 1'))
            db.session.commit()
        except Exception:
            return ResponseError(GeneralException.DatabaseConnection()).json()

    @app.before_request
    def check_http_endpoint_and_method() -> Response | None:
        method = request.method
        route = request.path

        adapter = app.url_map.bind('')
        try:
            adapter.match(route, method)
        except MethodNotAllowed:
            return ResponseError(GeneralException.MethodNotAllowed()).json()
        except NotFound:
            return ResponseError((GeneralException.EnpointNotFound())).json()

    @app.before_request
    def check_content_type() -> Response | None:
        allowed_content_types = 'multipart/form-data', 'application/json'

        if request.content_length and all(
            allowed_content_type not in request.content_type
            for allowed_content_type in allowed_content_types
        ):
            return ResponseError(GeneralException.InvalidContentType()).json()

    @app.before_request
    def check_options_request() -> Response | None:
        if request.method == 'OPTIONS':
            return ResponseSuccess().json()