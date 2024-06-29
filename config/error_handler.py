from flask import Flask, Response

from exception.base import ApiException
from response import ErrorResponse


def add_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiException)
    def handle_exceptions(e) -> Response:
        return ErrorResponse(e).json()
