from typing import Sequence

from dto.input import SearchDTO
from model import Book
from repository import SearchRepository


class SearchController:
    repository = SearchRepository()

    def search_books(self, input_dto: SearchDTO) -> Sequence[Book]:
        return self.repository.search(input_dto.query, input_dto.filter)
