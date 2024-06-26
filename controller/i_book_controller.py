from abc import ABC, abstractmethod
from typing import Sequence

from dto.input import CreateBookInputDTO, UpdateBookInputDTO
from model import Book


class IBookController(ABC):
    @abstractmethod
    def get_all_books(self) -> Sequence[Book]:
        pass

    @abstractmethod
    def get_book_by_id(self, id: str) -> Book:
        pass

    @abstractmethod
    def create_book(self, input_dto: CreateBookInputDTO) -> Book:
        pass

    @abstractmethod
    def delete_book(self, id: str) -> None:
        pass

    @abstractmethod
    def update_book(self, id: str, input_dto: UpdateBookInputDTO) -> Book:
        pass
