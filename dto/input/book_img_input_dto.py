from typing import Any

from flask import current_app
from pydantic import ConfigDict, field_validator
from werkzeug.datastructures import FileStorage

from dto.base import InputDTO
from exception import ImageException
from utils.file.uploader import BookImageUploader
from utils.file.validator import BookImageValidator


class BookImgInputDTO(InputDTO):
    img: BookImageUploader

    model_config = ConfigDict(arbitrary_types_allowed=True, extra='forbid')

    @field_validator('img', mode='plain')
    @classmethod
    def cast_img_to_UserImageUploader(cls, img: Any) -> BookImageUploader:
        if not BookImageValidator.is_a_file(img):
            raise ImageException.ImageIsNotAFile()

        if not BookImageValidator.has_valid_extension(img):
            raise ImageException.FileIsNotAnImage

        if not BookImageValidator.has_valid_size(img):
            max_file_size: int = current_app.config["BOOK_PHOTOS_MAX_SIZE"] // int(1e6)

            raise ImageException.ImageIsTooLarge(max_file_size)

        return BookImageUploader(img)

    def __init__(self, **data: FileStorage | Any) -> None:
        super().__init__(**data)
