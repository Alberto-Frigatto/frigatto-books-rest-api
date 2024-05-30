from flask import Blueprint, Response, send_file
from flask_jwt_extended import jwt_required, set_access_cookies, unset_jwt_cookies
from flask_restful import Api

from api import BaseResource
from controller import UserController
from exception.base import ApiException
from response import ResponseError, ResponseSuccess
from schema import users_schema

users_bp = Blueprint('users_bp', __name__)
users_api = Api(users_bp)

controller = UserController()


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
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = users_schema.dump(new_user)

            return ResponseSuccess(data, 201).json()

    @jwt_required()
    def patch(self) -> Response:
        try:
            updated_user = controller.update_user()
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = users_schema.dump(updated_user)
            return ResponseSuccess(data).json()


class UsersLoginView(BaseResource):
    @jwt_required(optional=True)
    def post(self) -> Response:
        try:
            user, access_token = controller.login()
        except ApiException as e:
            return ResponseError(e).json()
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


class UsersPhotosView(BaseResource):
    def get(self, filename: str) -> Response:
        try:
            file_path, mimetype = controller.get_user_photo(filename)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            return send_file(file_path, mimetype)


users_api.add_resource(UsersView, '')
users_api.add_resource(UsersLoginView, '/login')
users_api.add_resource(UsersLogoutView, '/logout')
users_api.add_resource(UsersPhotosView, '/photos/<string:filename>')
