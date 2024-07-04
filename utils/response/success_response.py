from typing import Any

import flask

from .base import Response


class SuccessResponse(Response):
    def __init__(self, data: dict[str, Any] | None = None, status: int = 200) -> None:
        self._status = status
        self._data = data

    def json(self) -> flask.Response:
        response = {
            'error': False,
            'status': self._status,
        }

        if self._data is not None:
            response['data'] = self._data

        return super()._make_response(response, self._status)
