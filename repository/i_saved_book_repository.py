from abc import ABC, abstractmethod

from flask_sqlalchemy.pagination import Pagination

from model import Book, SavedBook


class ISavedBookRepository(ABC):
    @abstractmethod
    def get_all(self, page: int) -> Pagination:
        pass

    @abstractmethod
    def get_by_id_book(self, id_book: str) -> SavedBook:
        pass

    @abstractmethod
    def add(self, saved_book: SavedBook) -> None:
        pass

    @abstractmethod
    def delete(self, saved_book: SavedBook) -> None:
        pass
