from typing import Sequence

from dto.input import SearchInputDTO
from model import Book
from repository import SearchRepository


class SearchController:
    repository = SearchRepository()

    def search_books(self, input_dto: SearchInputDTO) -> Sequence[Book]:
        return self.repository.search(
            query=input_dto.query,
            id_book_genre=input_dto.id_book_genre,
            id_book_kind=input_dto.id_book_kind,
            release_year=input_dto.release_year,
            min_price=input_dto.min_price,
            max_price=input_dto.max_price,
        )
