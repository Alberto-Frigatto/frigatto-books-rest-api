from abc import ABCMeta, abstractmethod
from typing import Any

import flask
from flask import current_app, jsonify


class Response(metaclass=ABCMeta):
    @abstractmethod
    def json(self) -> flask.Response:
        pass

    def _make_response(self, response_data: dict[str, Any], status: int) -> flask.Response:
        response = jsonify(response_data)

        self._add_headers(response)
        response.status = str(status)

        return response

    def _add_headers(self, response: flask.Response) -> None:
        for header, value in current_app.config['RESPONSE_HEADERS']:
            response.headers.add(header, value)
