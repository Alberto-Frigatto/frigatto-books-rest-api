import os
from typing import Any

from flask import current_app, request
from flask_jwt_extended import create_access_token, current_user
from sqlalchemy import select

from db import db
from handle_errors import CustomError
from image_uploaders import UsersImageUploader
from models import User

from .controller import Controller

token = str
file_path = str
mimetype = str


class UsersController(Controller):
    def create_user(self) -> User:
        if self._user_already_authenticated():
            raise CustomError('UserAlreadyAuthenticated')

        if not super()._are_there_data():
            raise CustomError('NoDataSent')

        form_data = request.form.to_dict()
        files_data = request.files.to_dict()

        if not self._is_data_valid_for_create(form_data, files_data):
            raise CustomError('InvalidDataSent')

        if self._user_already_exists(form_data['username']):
            raise CustomError('UserAlreadyExists')

        image_uploader = UsersImageUploader(files_data['img'])

        new_user = User(form_data['username'], form_data['password'], image_uploader.get_url())

        image_uploader.save()

        db.session.add(new_user)
        db.session.commit()

        return new_user

    def _user_already_authenticated(self) -> bool:
        return bool(current_user)

    def _is_data_valid_for_create(self, form_data: dict, files_data: dict) -> bool:
        return (
            all(key in form_data.keys() for key in ('username', 'password'))
            and 'img' in files_data.keys()
        )

    def _user_already_exists(self, username: Any) -> bool:
        query = select(User).where(
            User.username.ilike(username.strip().lower() if isinstance(username, str) else username)
        )

        return bool(db.session.execute(query).scalar())

    def login(self) -> tuple[User, token]:
        if self._user_already_authenticated():
            raise CustomError('UserAlreadyAuthenticated')

        if not super()._are_there_data():
            raise CustomError('NoDataSent')

        data = request.json

        if not self._is_data_valid_for_login(data):
            raise CustomError('InvalidDataSent')

        user = self._get_user_by_username(data['username'])

        if user is None or not user.check_password(data['password']):
            raise CustomError('InvalidLogin')

        access_token = create_access_token(user)

        return user, access_token

    def _is_data_valid_for_login(self, data: Any) -> bool:
        return isinstance(data, dict) and all(
            key in data.keys() for key in ('username', 'password')
        )

    def _get_user_by_username(self, username: Any) -> User | None:
        query = select(User).filter_by(username=username)

        return db.session.execute(query).scalar()

    def get_current_user(self) -> User:
        return current_user

    def get_user_photo(self, filename: str) -> tuple[file_path, mimetype]:
        if not self._is_file_name_valid(filename):
            raise CustomError('ImageNotFound')

        return os.path.join(current_app.config['USER_PHOTOS_UPLOAD_DIR'], filename), 'image/jpeg'

    def _is_file_name_valid(self, filename: str) -> bool:
        return (
            isinstance(filename, str)
            and filename.endswith('.jpg')
            and os.path.isfile(os.path.join(current_app.config['USER_PHOTOS_UPLOAD_DIR'], filename))
        )

    def update_user(self) -> User:
        if not super()._are_there_data():
            raise CustomError('NoDataSent')

        form_data = request.form.to_dict()
        files_data = request.files.to_dict()

        if not self._is_data_valid_for_update(form_data, files_data):
            raise CustomError('InvalidDataSent')

        if self._are_there_username_in_request(form_data) and self._user_already_exists(
            form_data['username']
        ):
            raise CustomError('UserAlreadyExists')

        for key, value in list(form_data.items()):
            getattr(current_user, f'update_{key.strip()}')(value)

        if self._are_there_image_in_request(files_data):
            self._replace_image_and_img_url(files_data)

        db.session.commit()

        return current_user

    def _is_data_valid_for_update(self, form_data: dict, files_data: dict) -> bool:
        files_keys = files_data.keys()

        allowed_keys = ('username', 'password')

        return 'img_url' not in files_keys and (
            all(key in allowed_keys for key in form_data.keys()) or 'img' in files_keys
        )

    def _replace_image_and_img_url(self, files_data: dict) -> None:
        image_uploader = UsersImageUploader(files_data['img'])

        UsersImageUploader.delete(current_user.img_url)

        current_user.update_img_url(image_uploader.get_url())

        image_uploader.save()

    def _are_there_image_in_request(self, files_data: dict) -> bool:
        return 'img' in files_data.keys()

    def _are_there_username_in_request(self, form_data: dict) -> bool:
        return 'username' in form_data.keys()
