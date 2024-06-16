from typing import Annotated, Any

from pydantic import StringConstraints

from dto.base import InputDTO


class BookKindInputDTO(InputDTO):
    kind: Annotated[
        str,
        StringConstraints(
            strict=True,
            strip_whitespace=True,
            to_lower=True,
            min_length=3,
            max_length=30,
            pattern=r'^[a-zA-ZÀ-ÿç\s]+$',
        ),
    ]

    def __init__(self, **data: str | Any) -> None:
        super().__init__(**data)
