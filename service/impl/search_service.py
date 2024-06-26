from typing import Sequence

from injector import inject

from dto.input import SearchInputDTO
from model import Book
from repository import ISearchRepository

from .. import ISearchService


@inject
class SearchService(ISearchService):
    def __init__(self, repository: ISearchRepository) -> None:
        self.repository = repository

    def search_books(self, input_dto: SearchInputDTO) -> Sequence[Book]:
        return self.repository.search(
            query=input_dto.query,
            id_book_genre=input_dto.id_book_genre,
            id_book_kind=input_dto.id_book_kind,
            release_year=input_dto.release_year,
            min_price=input_dto.min_price,
            max_price=input_dto.max_price,
        )
