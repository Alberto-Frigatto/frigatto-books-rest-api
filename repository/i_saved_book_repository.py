from abc import ABC, abstractmethod
from typing import Sequence

from model import Book, SavedBook


class ISavedBookRepository(ABC):
    @abstractmethod
    def get_all(self) -> Sequence[Book]:
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
