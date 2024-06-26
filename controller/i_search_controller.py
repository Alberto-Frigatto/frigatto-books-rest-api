from abc import ABC, abstractmethod
from typing import Sequence

from dto.input import SearchInputDTO
from model import Book


class ISearchController(ABC):
    @abstractmethod
    def search_books(self, input_dto: SearchInputDTO) -> Sequence[Book]:
        pass
