from typing import Any

from werkzeug.datastructures import FileStorage, ImmutableMultiDict

from dto.base import InputDTO
from dto.constraints import ImageConstraints, StrConstraints
from exception import GeneralException
from image_uploader import UserImageUploader


class UpdateUserDTO(InputDTO):
    username: str | None
    password: str | None
    img: UserImageUploader | None

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
        form_data: dict = data['form']
        files_data: ImmutableMultiDict = data['files']
        fields = self.__annotations__.keys()

        if all(field in filter(lambda x: x != 'img', fields) for field in form_data):
            if files_data:
                return all(field in fields for field in files_data)
            return True

        return False

    def _is_username_valid(self, username: Any) -> bool:
        return username is None or (
            isinstance(username, str)
            and StrConstraints.between_size(username.strip(), min_size=5, max_size=50)
            and StrConstraints.match_pattern(username.strip(), r'^[a-zA-Z\d_-]+$')
        )

    def _is_password_valid(self, password: Any) -> bool:
        return password is None or (
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
        return img is None or (
            isinstance(img, FileStorage)
            and ImageConstraints.valid_image(img, UserImageUploader.validate_file)
        )

    def _set_fields(self, data: dict) -> None:
        form_data: dict[str, str] = data['form']
        files_data: ImmutableMultiDict = data['files']

        self.username = (
            form_data['username'].strip() if form_data.get('username') is not None else None
        )
        self.password = (
            form_data['password'].strip() if form_data.get('password') is not None else None
        )
        self.img = (
            UserImageUploader(files_data['img']) if files_data.get('img') is not None else None
        )
