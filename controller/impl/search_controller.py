from flask_sqlalchemy.pagination import Pagination
from injector import inject

from dto.input import SearchInputDTO
from service import ISearchService

from .. import ISearchController


@inject
class SearchController(ISearchController):
    def __init__(self, service: ISearchService) -> None:
        self.service = service

    def search_books(self, page: int, input_dto: SearchInputDTO) -> Pagination:
        return self.service.search_books(page, input_dto)
