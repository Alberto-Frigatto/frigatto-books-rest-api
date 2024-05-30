import flask

from exception.base import ApiException

from .response import Response


class ResponseError(Response):
    def __init__(self, exception: ApiException) -> None:
        self._exception = exception

    def json(self) -> flask.Response:
        status = self._exception.status

        response = {
            'error': True,
            'error_name': self._exception.name,
            'message': self._exception.message,
            'status': status,
        }

        return self._make_response(response, status)
