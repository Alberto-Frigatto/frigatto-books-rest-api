from flask import Blueprint, Response
from flask_jwt_extended import jwt_required, set_access_cookies, unset_jwt_cookies
from flask_restful import Api

from api import BaseResource, api
from controllers import UsersController
from handle_errors import CustomError
from response import ResponseError, ResponseSuccess
from schemas import users_schema

users_bp = Blueprint('users_bp', __name__)
users_api = Api(users_bp)

controller = UsersController()


class UsersView(BaseResource):
    @jwt_required()
    def get(self) -> Response:
        current_user = controller.get_current_user()
        data = users_schema.dump(current_user)

        return ResponseSuccess(data).json()

    @jwt_required(optional=True)
    def post(self) -> Response:
        try:
            new_user = controller.create_user()
        except CustomError as e:
            return ResponseError(api.errors.get(e.error_name)).json()
        else:
            data = users_schema.dump(new_user)

            return ResponseSuccess(data, 201).json()


class UsersLoginView(BaseResource):
    @jwt_required(optional=True)
    def post(self) -> Response:
        try:
            user, access_token = controller.login()
        except CustomError as e:
            return ResponseError(api.errors.get(e.error_name)).json()
        else:
            data = users_schema.dump(user)

            response = ResponseSuccess(data).json()

            set_access_cookies(response, access_token)

            return response


class UsersLogoutView(BaseResource):
    @jwt_required()
    def post(self) -> Response:
        response = ResponseSuccess().json()

        unset_jwt_cookies(response)

        return response


users_api.add_resource(UsersView, '')
users_api.add_resource(UsersLoginView, '/login')
users_api.add_resource(UsersLogoutView, '/logout')
