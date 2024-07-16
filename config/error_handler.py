from flask import Flask, Response

from exception import SecurityException
from exception.base import ApiException
from security import jwt
from utils.response import ErrorResponse


def add_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiException)
    def handle_exceptions(e: ApiException) -> Response:
        return ErrorResponse(e).json()

    @jwt.unauthorized_loader
    def unauthorized_callback(error_string: str) -> Response:
        error_map = {
            'CSRF double submit tokens do not match': 'InvalidCSRF',
            'Missing CSRF token': 'MissingCSRF',
            'Missing cookie "access_token_cookie"': 'MissingJWT',
            'Missing Authorization Header': 'MissingJWT',
        }

        exception: ApiException = getattr(SecurityException, error_map[error_string])()

        return ErrorResponse(exception).json()

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string: str) -> Response:
        return ErrorResponse(SecurityException.InvalidJWT()).json()
