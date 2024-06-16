import os

from flask import current_app
from flask_jwt_extended import current_user

from dto.input import CreateUserInputDTO, UpdateUserInputDTO
from exception import AuthException, ImageException
from image_uploader import UserImageUploader
from model import User
from repository import UserRepository

file_path = str
mimetype = str


class UserController:
    repository = UserRepository()

    def create_user(self, input_dto: CreateUserInputDTO) -> User:
        if self._user_already_authenticated():
            raise AuthException.UserAlreadyAuthenticated()

        new_user = User(input_dto.username, input_dto.password, input_dto.img.get_url())

        self.repository.add(new_user)

        input_dto.img.save()

        return new_user

    def _user_already_authenticated(self) -> bool:
        return bool(current_user)

    def get_current_user(self) -> User:
        return current_user

    def get_user_photo(self, filename: str) -> tuple[file_path, mimetype]:
        if not self._is_file_name_valid(filename):
            raise ImageException.ImageNotFound(filename)

        return os.path.join(current_app.config['USER_PHOTOS_UPLOAD_DIR'], filename), 'image/jpeg'

    def _is_file_name_valid(self, filename: str) -> bool:
        return filename.endswith('.jpg') and os.path.isfile(
            os.path.join(current_app.config['USER_PHOTOS_UPLOAD_DIR'], filename)
        )

    def update_user(self, input_dto: UpdateUserInputDTO) -> User:
        for key, value in input_dto.__dict__.items():
            if value is not None and key != 'img':
                getattr(current_user, f'update_{key.strip()}')(value)

        if input_dto.img is not None:
            self._swap_book_img(current_user.img_url, input_dto.img)

        self.repository.update(current_user)

        return current_user

    def _swap_book_img(self, old_img_url: str, new_img: UserImageUploader) -> None:
        UserImageUploader.delete(old_img_url)

        current_user.update_img_url(new_img.get_url())

        new_img.save()
