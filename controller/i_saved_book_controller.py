from abc import ABC, abstractmethod
from typing import Sequence

from model import Book


class ISavedBookController(ABC):
    @abstractmethod
    def get_all_saved_books(self) -> Sequence[Book]:
        pass

    @abstractmethod
    def save_book(self, id: str) -> Book:
        pass

    @abstractmethod
    def delete_saved_book(self, id_book: str) -> None:
        pass
