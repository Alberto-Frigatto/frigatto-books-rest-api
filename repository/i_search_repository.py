from abc import ABC, abstractmethod
from decimal import Decimal

from flask_sqlalchemy.pagination import Pagination


class ISearchRepository(ABC):
    @abstractmethod
    def search(
        self,
        *,
        page: int,
        query: str | None,
        id_book_kind: int | None,
        id_book_genre: int | None,
        release_year: int | None,
        min_price: Decimal | None,
        max_price: Decimal | None,
    ) -> Pagination:
        pass
