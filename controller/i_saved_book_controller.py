from abc import ABC, abstractmethod

from flask_sqlalchemy.pagination import Pagination

from model import Book


class ISavedBookController(ABC):
    @abstractmethod
    def get_all_saved_books(self, page: int) -> Pagination:
        pass

    @abstractmethod
    def save_book(self, id: str) -> Book:
        pass

    @abstractmethod
    def delete_saved_book(self, id_book: str) -> None:
        pass
