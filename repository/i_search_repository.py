from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Sequence

from model import Book


class ISearchRepository(ABC):
    @abstractmethod
    def search(
        self,
        *,
        query: str | None,
        id_book_kind: int | None,
        id_book_genre: int | None,
        release_year: int | None,
        min_price: Decimal | None,
        max_price: Decimal | None,
    ) -> Sequence[Book]:
        pass
