from typing import Annotated, Any

from flask import current_app
from pydantic import ConfigDict, StringConstraints, field_validator
from werkzeug.datastructures import FileStorage

from dto.base import InputDTO
from exception import ImageException, UserException
from utils.file.uploader import UserImageUploader
from utils.file.validator import UserImageValidator


class CreateUserInputDTO(InputDTO):
    username: Annotated[
        str,
        StringConstraints(
            strict=True,
            strip_whitespace=True,
            min_length=4,
            max_length=50,
            pattern=r'^[a-zA-Z\d_-]+$',
        ),
    ]
    password: Annotated[
        str,
        StringConstraints(
            strict=True,
            strip_whitespace=True,
            min_length=8,
            max_length=255,
        ),
    ]
    img: UserImageUploader

    model_config = ConfigDict(arbitrary_types_allowed=True, extra='forbid')

    @field_validator('password', mode='plain')
    @classmethod
    def password_has_necessary_length_and_chars(cls, password: str) -> str:
        min_chars = 8
        if len(password) < min_chars:
            raise UserException.PasswordTooShort(min_chars)

        max_chars = 255
        if len(password) > max_chars:
            raise UserException.PasswordTooLong(max_chars)

        has_uppercase = any(char.isupper() for char in password)
        has_lowercase = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_special = any(char in "!@#$%&*()_+=-,.:;?/\\|" for char in password)

        if not all((has_uppercase, has_lowercase, has_digit, has_special)):
            raise UserException.PasswordWithoutNecessaryChars()

        return password

    @field_validator('img', mode='plain')
    @classmethod
    def cast_img_to_UserImageUploader(cls, img: Any) -> UserImageUploader:
        if not UserImageValidator.is_a_file(img):
            raise ImageException.ImageIsNotAFile()

        if not UserImageValidator.has_valid_extension(img):
            raise ImageException.FileIsNotAnImage

        if not UserImageValidator.has_valid_size(img):
            max_file_size: int = current_app.config["USER_PHOTOS_MAX_SIZE"] // int(1e6)

            raise ImageException.ImageIsTooLarge(max_file_size)

        return UserImageUploader(img)

    def __init__(self, **data: str | FileStorage) -> None:
        super().__init__(**data)
