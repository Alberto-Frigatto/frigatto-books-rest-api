from os.path import isfile
from typing import Any

from flask import request
from flask_jwt_extended import create_access_token, current_user
from sqlalchemy import select

from db import db
from handle_errors import CustomError
from image_uploaders import UsersPhotoImageUploader
from models import User

token = str
file_path = str
mimetype = str


class UsersController:
    def create_user(self) -> User:
        if self._user_already_authenticated():
            raise CustomError('UserAlreadyAuthenticated')

        if not self._are_there_data():
            raise CustomError('NoDataSent')

        form_data = request.form.to_dict()
        files_data = request.files.to_dict()

        if not self._is_data_valid_for_create(form_data, files_data):
            raise CustomError('InvalidDataSent')

        if self._user_already_exists(form_data['username']):
            raise CustomError('UserAlreadyExists')

        image_uploader = UsersPhotoImageUploader(files_data['img'])

        new_user = User(form_data['username'], form_data['password'], image_uploader.get_url())

        image_uploader.save()

        db.session.add(new_user)
        db.session.commit()

        return new_user

    def _user_already_authenticated(self) -> bool:
        return bool(current_user)

    def _are_there_data(self) -> bool:
        return request.content_length

    def _is_data_valid_for_create(self, form_data: Any, files_data) -> bool:
        return (
            isinstance(form_data, dict)
            and 'username' in form_data.keys()
            and 'password' in form_data.keys()
            and isinstance(files_data, dict)
            and 'img' in files_data.keys()
        )

    def _user_already_exists(self, username: str) -> bool:
        return bool(db.session.execute(select(User).filter_by(username=username)).scalar())

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
