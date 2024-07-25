from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import ConfigDict, Field, StringConstraints
from werkzeug.datastructures import FileStorage

from dto.base import InputDTO


class UpdateBookInputDTO(InputDTO):
    name: Optional[
        Annotated[
            str,
            StringConstraints(
                strict=True,
                strip_whitespace=True,
                min_length=2,
                max_length=80,
                pattern=r'^[a-zA-ZÀ-ÿç\s\d-]+$',
            ),
        ]
    ] = None
    price: Optional[Annotated[Decimal, Field(gt=0, max_digits=6, decimal_places=2)]] = None
    author: Optional[
        Annotated[
            str,
            StringConstraints(
                strict=True,
                strip_whitespace=True,
                min_length=3,
                max_length=40,
                pattern=r'^[a-zA-ZÀ-ÿç\s]+$',
            ),
        ]
    ] = None
    release_year: Optional[Annotated[int, Field(ge=1000, le=datetime.now().year)]] = None
    id_book_kind: Optional[Annotated[int, Field(gt=0)]] = None
    id_book_genre: Optional[Annotated[int, Field(gt=0)]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True, extra='forbid')

    def __init__(self, **data: str | list[FileStorage]) -> None:
        super().__init__(**data)
