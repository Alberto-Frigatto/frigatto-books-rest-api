from abc import ABCMeta, abstractmethod
from typing import Any

import flask
from flask import current_app, jsonify


class Response(metaclass=ABCMeta):
    @abstractmethod
    def json(self) -> flask.Response:
        pass

    def _make_response(self, *, payload: dict[str, Any] | None, status: int) -> flask.Response:
        response = jsonify(payload)

        self._add_headers(response)
        response.status = str(status)

        return response

    def _add_headers(self, response: flask.Response) -> None:
        for header, value in current_app.config['RESPONSE_HEADERS']:
            response.headers.add(header, value)
