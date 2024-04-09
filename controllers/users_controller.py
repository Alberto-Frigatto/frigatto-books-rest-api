from typing import Any

from flask import request
from flask_jwt_extended import create_access_token, current_user
from sqlalchemy import select

from db import db
from handle_errors import CustomError
from models import User

token = str


class UsersController:
    def create_user(self) -> User:
        if self._user_already_authenticated():
            raise CustomError('UserAlreadyAuthenticated')

        if not self._are_there_data():
            raise CustomError('NoDataSent')

        data = request.json

        if not self._is_data_valid(data):
            raise CustomError('InvalidDataSent')

        new_user = User(data['username'], data['password'])

        if self._user_already_exists(new_user):
            raise CustomError('UserAlreadyExists')

        db.session.add(new_user)
        db.session.commit()

        return new_user

    def _user_already_authenticated(self) -> bool:
        return bool(current_user)

    def _are_there_data(self) -> bool:
        return request.content_length

    def _is_data_valid(self, data: Any) -> bool:
        return isinstance(data, dict) and 'username' in data.keys() and 'password' in data.keys()

    def _user_already_exists(self, user: User) -> bool:
        return bool(db.session.execute(select(User).filter_by(username=user.username)).scalar())

    def login(self) -> tuple[User, token]:
        if self._user_already_authenticated():
            raise CustomError('UserAlreadyAuthenticated')

        if not self._are_there_data():
            raise CustomError('NoDataSent')

        data = request.json

        if not self._is_data_valid(data):
            raise CustomError('InvalidDataSent')

        user = db.session.execute(
            select(User).filter_by(username=data['username'])
        ).scalar_one_or_none()

        if user is None or not user.check_password(data['password']):
            raise CustomError('InvalidLogin')

        access_token = create_access_token(user)

        return user, access_token

    def get_current_user(self) -> User:
        return current_user
