from flask import Blueprint, Response
from flask_jwt_extended import jwt_required, set_access_cookies, unset_jwt_cookies

from controller import AuthController
from dto.input import LoginInputDTO
from dto.output import UserOutputDTO
from request import Request
from response import ResponseSuccess

auth_bp = Blueprint('auth_bp', __name__)


class AuthView:
    @staticmethod
    @auth_bp.post('/login')
    @jwt_required(optional=True)
    def login(controller: AuthController) -> Response:
        input_dto = LoginInputDTO(**Request.get_json())
        user, access_token = controller.login(input_dto)
        data = UserOutputDTO.dump(user)

        response = ResponseSuccess(data).json()
        set_access_cookies(response, access_token)

        return response

    @staticmethod
    @auth_bp.post('/logout')
    @jwt_required()
    def logout() -> Response:
        response = ResponseSuccess().json()

        unset_jwt_cookies(response)

        return response
