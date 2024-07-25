import flask

from exception.base import ApiException

from .base import Response


class ErrorResponse(Response):
    def __init__(self, exception: ApiException) -> None:
        self._exception = exception

    def json(self) -> flask.Response:
        return super()._make_response(
            payload=self._exception.searialize(),
            status=self._exception.status,
        )
