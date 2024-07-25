from abc import ABC, abstractmethod

from flask_sqlalchemy.pagination import Pagination

from dto.input import SearchInputDTO


class ISearchController(ABC):
    @abstractmethod
    def search_books(self, page: int, input_dto: SearchInputDTO) -> Pagination:
        pass
