from flask import Blueprint, Response
from flask_jwt_extended import jwt_required, set_access_cookies, unset_jwt_cookies

from controller import IAuthController
from dto.input import LoginInputDTO
from dto.output import UserOutputDTO
from utils.request import Request
from utils.response import NoContentResponse, OkResponse

auth_bp = Blueprint('auth_bp', __name__)


class AuthView:
    @staticmethod
    @auth_bp.post('/login')
    @jwt_required(optional=True)
    def login(controller: IAuthController) -> Response:
        input_dto = LoginInputDTO(**Request.get_json())
        user, access_token = controller.login(input_dto)
        data = UserOutputDTO.dump(user)

        response = OkResponse(data).json()
        set_access_cookies(response, access_token)

        return response

    @staticmethod
    @auth_bp.get('/logout')
    def logout() -> Response:
        response = NoContentResponse().json()
        unset_jwt_cookies(response)

        return response
