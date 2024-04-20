import flask

from handle_errors import CustomError

from .response import Response


class ResponseError(Response):
    def __init__(self, error: CustomError) -> None:
        from api import api

        self._api_error = api.errors.get(error.error_name)
        self._error_name = error.error_name

    def json(self) -> flask.Response:
        status = self._api_error['status']

        response = {
            'error': True,
            'error_name': self._error_name,
            'message': self._api_error['message'],
            'status': status,
        }

        return self._make_response(response, status)
