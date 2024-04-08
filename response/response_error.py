import flask

from .response import Response


class ResponseError(Response):
    def __init__(self, api_error: dict) -> None:
        self._api_error = api_error

    def json(self) -> flask.Response:
        status = self._api_error['status']

        response = {
            'error': True,
            'message': self._api_error['message'],
            'status': status,
        }

        return self._make_response(response, status)
