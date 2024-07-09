import os

from flask import current_app
from flask_jwt_extended import current_user
from injector import inject

from dto.input import CreateUserInputDTO, UpdateUserInputDTO
from exception import AuthException, ImageException
from model import User
from repository import IUserRepository
from utils.file.uploader import UserImageUploader

from .. import IUserService

file_path = str
mimetype = str


@inject
class UserService(IUserService):
    def __init__(self, repository: IUserRepository) -> None:
        self.repository = repository

    def create_user(self, input_dto: CreateUserInputDTO) -> User:
        if self._user_already_authenticated():
            raise AuthException.UserAlreadyAuthenticated()

        new_user = User(input_dto.username, input_dto.password, input_dto.img.get_url())

        self.repository.add(new_user)
        input_dto.img.save()

        return new_user

    def _user_already_authenticated(self) -> bool:
        return bool(self.get_current_user())

    def get_current_user(self) -> User:
        return current_user

    def get_user_photo(self, filename: str) -> tuple[file_path, mimetype]:
        file_path = os.path.join(current_app.config['USER_PHOTOS_UPLOAD_DIR'], filename)

        if not self._is_file_path_valid(file_path):
            raise ImageException.ImageNotFound(filename)

        return file_path, 'image/jpeg'

    def _is_file_path_valid(self, file_path: str) -> bool:
        return os.path.isfile(file_path)

    def update_user(self, input_dto: UpdateUserInputDTO) -> User:
        for key, value in input_dto.items:
            if value is not None and key != 'img':
                getattr(current_user, f'update_{key.strip()}')(value)

        old_img_url: str | None = None
        if input_dto.img is not None:
            old_img_url = current_user.img_url
            current_user.update_img_url(input_dto.img.get_url())

        self.repository.update(current_user)

        if old_img_url is not None and input_dto.img is not None:
            UserImageUploader.delete(old_img_url)
            input_dto.img.save()

        return current_user
