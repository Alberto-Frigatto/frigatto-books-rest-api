import flask

from .base import Response


class NoContentResponse(Response):
    def json(self) -> flask.Response:
        return super()._make_response(payload=None, status=204)
