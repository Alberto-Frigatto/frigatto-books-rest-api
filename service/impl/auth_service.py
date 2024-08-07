from flask_jwt_extended import create_access_token, current_user
from injector import inject

from dto.input import LoginInputDTO
from exception import AuthException
from model import User
from repository import IUserRepository

from .. import IAuthService

token = str


@inject
class AuthService(IAuthService):
    def __init__(self, repository: IUserRepository) -> None:
        self.repository = repository

    def login(self, input_dto: LoginInputDTO) -> tuple[User, token]:
        if self._user_already_authenticated():
            raise AuthException.UserAlreadyAuthenticated()

        user = self.repository.get_by_username(input_dto.username)

        if user is None or not user.check_password(input_dto.password):
            raise AuthException.InvalidLogin()

        access_token = create_access_token(user)

        return user, access_token

    def _user_already_authenticated(self) -> bool:
        return bool(current_user)
