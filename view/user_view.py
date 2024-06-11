from flask import Blueprint, Response, send_file
from flask_jwt_extended import jwt_required

from controller import UserController
from dto.input import CreateUserDTO, UpdateUserDTO
from exception.base import ApiException
from response import ResponseError, ResponseSuccess
from schema import users_schema

user_bp = Blueprint('user_bp', __name__)


class UserView:
    controller = UserController()

    @staticmethod
    @user_bp.get('')
    @jwt_required()
    def get_user_info() -> Response:
        current_user = UserView.controller.get_current_user()
        data = users_schema.dump(current_user)

        return ResponseSuccess(data).json()

    @staticmethod
    @user_bp.post('')
    @jwt_required(optional=True)
    def create_user() -> Response:
        try:
            input_dto = CreateUserDTO()
            new_user = UserView.controller.create_user(input_dto)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = users_schema.dump(new_user)

            return ResponseSuccess(data, 201).json()

    @staticmethod
    @user_bp.patch('')
    @jwt_required()
    def update_user() -> Response:
        try:
            input_dto = UpdateUserDTO()
            updated_user = UserView.controller.update_user(input_dto)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = users_schema.dump(updated_user)
            return ResponseSuccess(data).json()

    @staticmethod
    @user_bp.get('/photos/<filename>')
    def get_user_photo(filename: str) -> Response:
        try:
            file_path, mimetype = UserView.controller.get_user_photo(filename)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            return send_file(file_path, mimetype)
