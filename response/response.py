from abc import ABCMeta, abstractmethod
from typing import Any

import flask
from flask import jsonify


class Response(metaclass=ABCMeta):
    @abstractmethod
    def json(self) -> flask.Response:
        pass

    def _make_response(self, response: Any, status: int) -> flask.Response:
        out_response = jsonify(response)

        out_response.headers.add('Content-Type', 'application/json;charset=utf-8')
        out_response.headers.add('Access-Control-Allow-Origin', '*')
        out_response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        out_response.status = status

        return out_response
