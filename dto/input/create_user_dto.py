from typing import Any

from werkzeug.datastructures import FileStorage, ImmutableMultiDict

from dto.base import InputDTO
from dto.constraints import ImageConstraints, StrConstraints
from exception import GeneralException
from image_uploader import UserImageUploader


class CreateUserDTO(InputDTO):
    username: str
    password: str
    img: UserImageUploader

    def __init__(self) -> None:
        data = {
            'form': super()._get_form_data(),
            'files': super()._get_files_data(),
        }
        self._validate_data(data)
        self._set_fields(data)

    def _validate_data(self, data: dict) -> None:
        form_data: dict = data['form']
        files_data: ImmutableMultiDict = data['files']

        username = form_data.get('username')
        password = form_data.get('password')
        img: FileStorage | None = files_data.get('img')

        if not all(
            (
                self._are_request_fields_valid(data),
                self._is_username_valid(username),
                self._is_password_valid(password),
                self._is_img_valid(img),
            )
        ):
            raise GeneralException.InvalidDataSent()

    def _are_request_fields_valid(self, data: dict) -> bool:
        fields = self.__annotations__.keys()
        form_data: dict = data['form']
        files_data: ImmutableMultiDict = data['files']

        return all(field in fields for field in form_data) and all(
            field in fields for field in files_data
        )

    def _is_username_valid(self, username: Any) -> bool:
        return (
            isinstance(username, str)
            and StrConstraints.between_size(username.strip(), min_size=4, max_size=50)
            and StrConstraints.match_pattern(username.strip(), r'^[a-zA-Z\d_-]+$')
        )

    def _is_password_valid(self, password: Any) -> bool:
        return (
            isinstance(password, str)
            and StrConstraints.between_size(password.strip(), min_size=8, max_size=255)
            and self._password_has_necessary_chars(password)
        )

    def _password_has_necessary_chars(self, password: str) -> bool:
        has_uppercase = any(char.isupper() for char in password)
        has_lowercase = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_special = any(char in "!@#$%&*()_+=-,.:;?/\\|" for char in password)

        return all((has_uppercase, has_lowercase, has_digit, has_special))

    def _is_img_valid(self, img: FileStorage | None) -> bool:
        return isinstance(img, FileStorage) and ImageConstraints.valid_image(
            img, UserImageUploader.validate_file
        )

    def _set_fields(self, data: dict) -> None:
        form_data: dict[str, str] = data['form']
        files_data: ImmutableMultiDict = data['files']

        self.username = form_data['username'].strip()
        self.password = form_data['password'].strip()
        self.img = UserImageUploader(files_data['img'])
