from typing import Any

import flask

from .base import Response


class OkResponse(Response):
    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def json(self) -> flask.Response:
        return super()._make_response(payload=self._data, status=200)
