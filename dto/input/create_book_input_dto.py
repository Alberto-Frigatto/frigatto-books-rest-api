from datetime import datetime
from decimal import Decimal
from typing import Annotated

from flask import current_app
from pydantic import ConfigDict, Field, StringConstraints, field_validator
from pydantic.functional_validators import AfterValidator
from werkzeug.datastructures import FileStorage

from dto.base import InputDTO
from exception import BookException, BookKeywordException, ImageException
from utils.file.uploader import BookImageUploader
from utils.file.validator import BookImageValidator


def validate_img(img_uploader: BookImageUploader) -> BookImageUploader:
    if not BookImageValidator.has_valid_extension(img_uploader.file):
        raise ImageException.FileIsNotAnImage()

    if not BookImageValidator.has_valid_size(img_uploader.file):
        max_file_size: int = current_app.config["BOOK_PHOTOS_MAX_SIZE"] // int(1e6)

        raise ImageException.ImageIsTooLarge(max_file_size)

    return img_uploader


class CreateBookInputDTO(InputDTO):
    name: Annotated[
        str,
        StringConstraints(
            strict=True,
            strip_whitespace=True,
            min_length=2,
            max_length=80,
            pattern=r'^[a-zA-ZÀ-ÿç\s\d-]+$',
        ),
    ]
    price: Annotated[Decimal, Field(gt=0, max_digits=6, decimal_places=2)]
    author: Annotated[
        str,
        StringConstraints(
            strict=True,
            strip_whitespace=True,
            min_length=3,
            max_length=40,
            pattern=r'^[a-zA-ZÀ-ÿç\s]+$',
        ),
    ]
    release_year: Annotated[int, Field(ge=1000, le=datetime.now().year)]
    keywords: list[
        Annotated[
            str,
            StringConstraints(
                strict=True,
                strip_whitespace=True,
                min_length=3,
                max_length=20,
                pattern=r'^[a-zA-ZÀ-ÿç\s\d]+$',
            ),
        ]
    ]
    id_book_kind: Annotated[int, Field(gt=0)]
    id_book_genre: Annotated[int, Field(gt=0)]
    imgs: list[Annotated[BookImageUploader, AfterValidator(validate_img)]]

    model_config = ConfigDict(arbitrary_types_allowed=True, extra='forbid')

    @field_validator('keywords', mode='before')
    @classmethod
    def cast_keywords_to_list_str(cls, keywords: str) -> list[str]:
        if not keywords:
            raise BookKeywordException.BookMustContainsAtLeastOneKeywordOnCreation()

        return [keyword.strip() for keyword in keywords.strip().split(';') if keyword]

    @field_validator('imgs', mode='before')
    @classmethod
    def cast_imgs_to_list_UserImageUploader(
        cls, imgs: list[FileStorage] | str
    ) -> list[BookImageUploader]:
        if not isinstance(imgs, list) or not all(BookImageValidator.is_a_file(img) for img in imgs):
            raise ImageException.ImagesArentFiles()

        min_qty = 1
        if len(imgs) < min_qty:
            raise BookException.BookImageListTooShort(min_qty)

        max_qty = current_app.config['BOOK_IMG_MAX_QTY']
        if len(imgs) > max_qty:
            raise BookException.BookImageListTooLong(max_qty)

        return [BookImageUploader(img) for img in imgs]

    def __init__(self, **data: str | list[FileStorage]) -> None:
        super().__init__(**data)
