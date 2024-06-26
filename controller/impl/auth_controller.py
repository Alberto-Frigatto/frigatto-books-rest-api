from injector import inject

from dto.input import LoginInputDTO
from model import User
from service import IAuthService

from .. import IAuthController

token = str


@inject
class AuthController(IAuthController):
    def __init__(self, service: IAuthService) -> None:
        self.service = service

    def login(self, input_dto: LoginInputDTO) -> tuple[User, token]:
        return self.service.login(input_dto)
