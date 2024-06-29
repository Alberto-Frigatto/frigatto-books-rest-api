from flask import Blueprint, Response
from flask_jwt_extended import jwt_required, set_access_cookies, unset_jwt_cookies

from controller import IAuthController
from dto.input import LoginInputDTO
from dto.output import UserOutputDTO
from request import Request
from response import SuccessResponse

auth_bp = Blueprint('auth_bp', __name__)


class AuthView:
    @staticmethod
    @auth_bp.post('/login')
    @jwt_required(optional=True)
    def login(controller: IAuthController) -> Response:
        input_dto = LoginInputDTO(**Request.get_json())
        user, access_token = controller.login(input_dto)
        data = UserOutputDTO.dump(user)

        response = SuccessResponse(data).json()
        set_access_cookies(response, access_token)

        return response

    @staticmethod
    @auth_bp.post('/logout')
    def logout() -> Response:
        response = SuccessResponse().json()

        unset_jwt_cookies(response)

        return response
