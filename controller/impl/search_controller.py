from typing import Sequence

from injector import inject

from dto.input import SearchInputDTO
from model import Book
from service import ISearchService

from .. import ISearchController


@inject
class SearchController(ISearchController):
    def __init__(self, service: ISearchService) -> None:
        self.service = service

    def search_books(self, input_dto: SearchInputDTO) -> Sequence[Book]:
        return self.service.search_books(input_dto)
