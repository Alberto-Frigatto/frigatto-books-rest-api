from flask import Blueprint, Response, redirect, send_file, url_for
from flask_jwt_extended import jwt_required
from werkzeug.wrappers.response import Response as WerkzeugResponse

from controller import IUserController
from dto.input import CreateUserInputDTO, UpdateUserInputDTO
from dto.output import UserOutputDTO
from utils.request import Request
from utils.response import CreatedResponse, OkResponse

user_bp = Blueprint('user_bp', __name__)


class UserView:
    @staticmethod
    @user_bp.get('')
    @jwt_required()
    def get_user_info(controller: IUserController) -> Response:
        current_user = controller.get_current_user()
        data = UserOutputDTO.dump(current_user)

        return OkResponse(data).json()

    @staticmethod
    @user_bp.post('')
    @jwt_required(optional=True)
    def create_user(controller: IUserController) -> Response:
        input_dto = CreateUserInputDTO(**Request.get_form(), **Request.get_files())

        new_user = controller.create_user(input_dto)
        data = UserOutputDTO.dump(new_user)

        return CreatedResponse(data).json()

    @staticmethod
    @user_bp.patch('')
    @jwt_required()
    def update_user(controller: IUserController) -> Response:
        input_dto = UpdateUserInputDTO(**Request.get_form(), **Request.get_files())

        updated_user = controller.update_user(input_dto)
        data = UserOutputDTO.dump(updated_user)

        return OkResponse(data).json()

    @staticmethod
    @user_bp.get('/photos/<filename>')
    def get_user_photo(filename: str, controller: IUserController) -> Response:
        file_path, mimetype = controller.get_user_photo(filename)

        return send_file(file_path, mimetype)

    @staticmethod
    @user_bp.delete('')
    @jwt_required()
    def delete_user(controller: IUserController) -> WerkzeugResponse:
        controller.delete_user()

        return redirect(url_for('auth.logout'))
