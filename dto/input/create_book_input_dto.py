from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import ConfigDict, Field, PositiveInt, StringConstraints, field_validator
from werkzeug.datastructures import FileStorage

from dto.base import InputDTO
from image_uploader import BookImageUploader


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
    id_book_kind: Annotated[int, PositiveInt]
    id_book_genre: Annotated[int, PositiveInt]
    imgs: list[BookImageUploader]

    model_config = ConfigDict(arbitrary_types_allowed=True, extra='forbid')

    @field_validator('keywords', mode='before')
    def cast_keywords_to_list_str(cls, keywords: str) -> list[str]:
        if not keywords:
            raise ValueError('Book must contains at least 1 keyword')

        return [keyword.strip() for keyword in keywords.strip().split(';') if keyword]

    @field_validator('imgs', mode='plain')
    def cast_imgs_to_list_UserImageUploader(
        cls, imgs: list[FileStorage]
    ) -> list[BookImageUploader]:
        if not 1 <= len(imgs) <= 5:
            raise ValueError('Book must contains at least 1 and a maximum 5 image')

        if not all(BookImageUploader.validate_file(img) for img in imgs):
            raise ValueError('img is larger than 7MB or is not a image')

        return [BookImageUploader(img) for img in imgs]

    def __init__(self, **data: str | list[FileStorage]) -> None:
        super().__init__(**data)
