from typing import Any

from flask_jwt_extended import create_access_token, current_user
from sqlalchemy import select

from db import db
from dto.input import LoginDTO
from exception import AuthException
from model import User

token = str


class AuthController:
    def login(self, input_dto: LoginDTO) -> tuple[User, token]:
        if self._user_already_authenticated():
            raise AuthException.UserAlreadyAuthenticated()

        user = self._get_user_by_username(input_dto.username)

        if user is None or not user.check_password(input_dto.password):
            raise AuthException.InvalidLogin()

        access_token = create_access_token(user)

        return user, access_token

    def _user_already_authenticated(self) -> bool:
        return bool(current_user)

    def _get_user_by_username(self, username: Any) -> User | None:
        query = select(User).filter_by(username=username)

        return db.session.execute(query).scalar()
