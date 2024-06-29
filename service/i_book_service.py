from abc import ABC, abstractmethod

from flask_sqlalchemy.pagination import Pagination

from dto.input import CreateBookInputDTO, UpdateBookInputDTO
from model import Book


class IBookService(ABC):
    @abstractmethod
    def get_all_books(self, page: int) -> Pagination:
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
