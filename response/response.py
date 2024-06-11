from abc import ABCMeta, abstractmethod

import flask
from flask import current_app, jsonify


class Response(metaclass=ABCMeta):
    @abstractmethod
    def json(self) -> flask.Response:
        pass

    def _make_response(self, response: dict, status: int) -> flask.Response:
        out_response = jsonify(response)

        for header, value in current_app.config['RESPONSE_HEADERS']:
            out_response.headers.add(header, value)

        out_response.status = str(status)

        return out_response
