from decimal import Decimal
from typing import Annotated, Any, Optional

from pydantic import Field

from dto.base import InputDTO


class SearchInputDTO(InputDTO):
    query: Optional[str] = None
    id_book_kind: Optional[Annotated[int, Field(gt=0)]] = None
    id_book_genre: Optional[Annotated[int, Field(gt=0)]] = None
    release_year: Optional[Annotated[int, Field(gt=0)]] = None
    min_price: Optional[Annotated[Decimal, Field(gt=0, max_digits=6, decimal_places=2)]] = None
    max_price: Optional[Annotated[Decimal, Field(gt=0, max_digits=6, decimal_places=2)]] = None

    def __init__(self, **data: str | int | float | Any) -> None:
        super().__init__(**data)
