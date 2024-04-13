from abc import ABCMeta, abstractmethod
from typing import Any

import flask
from flask import jsonify


class Response(metaclass=ABCMeta):
    @abstractmethod
    def json(self) -> flask.Response:
        pass

    def _make_response(self, response: Any, status: int) -> flask.Response:
        from app import app

        out_response = jsonify(response)

        for header, value in app.config['RESPONSE_HEADERS']:
            out_response.headers.add(header, value)

        out_response.status = status

        return out_response
