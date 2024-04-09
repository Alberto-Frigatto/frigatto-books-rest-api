from flask import Response
from flask_restful import Api, Resource

from response import ResponseSuccess

api = Api()


class BaseResource(Resource):
    def options(self, *args, **kwargs) -> Response:
        return ResponseSuccess().json()
