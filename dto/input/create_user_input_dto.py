from typing import Annotated, Any

from pydantic import ConfigDict, StringConstraints, field_validator
from werkzeug.datastructures import FileStorage

from dto.base import InputDTO
from image_uploader import UserImageUploader


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
    def password_has_necessary_chars(cls, password: str) -> str:
        has_uppercase = any(char.isupper() for char in password)
        has_lowercase = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_special = any(char in "!@#$%&*()_+=-,.:;?/\\|" for char in password)

        if not all((has_uppercase, has_lowercase, has_digit, has_special)):
            raise ValueError('password has not the necessary chars')

        return password

    @field_validator('img', mode='plain')
    def cast_img_to_UserImageUploader(cls, img: Any) -> UserImageUploader:
        if not isinstance(img, FileStorage):
            raise ValueError('img is not a file')

        if not UserImageUploader.validate_file(img):
            raise ValueError('img is larger than 5MB or is not a image')

        return UserImageUploader(img)

    def __init__(self, **data: str | FileStorage) -> None:
        super().__init__(**data)
