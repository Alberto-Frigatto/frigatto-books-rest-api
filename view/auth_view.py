from flask import Blueprint, Response
from flask_jwt_extended import jwt_required, set_access_cookies, unset_jwt_cookies

from controller import AuthController
from dto.input import LoginDTO
from exception.base import ApiException
from response import ResponseError, ResponseSuccess
from schema import users_schema

auth_bp = Blueprint('auth_bp', __name__)


class AuthView:
    controller = AuthController()

    @staticmethod
    @auth_bp.post('/login')
    @jwt_required(optional=True)
    def login() -> Response:
        try:
            input_dto = LoginDTO()
            user, access_token = AuthView.controller.login(input_dto)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = users_schema.dump(user)

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
