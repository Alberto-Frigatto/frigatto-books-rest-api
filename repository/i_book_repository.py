from abc import ABC, abstractmethod

from flask_sqlalchemy.pagination import Pagination

from model import Book


class IBookRepository(ABC):
    @abstractmethod
    def get_all(self, page: int) -> Pagination:
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> Book:
        pass

    @abstractmethod
    def add(self, book: Book) -> None:
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        pass

    @abstractmethod
    def update(self, book: Book) -> None:
        pass
