from abc import ABC, abstractmethod

from model import BookKeyword


class IBookKeywordRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> BookKeyword:
        pass

    @abstractmethod
    def add(self, book_keyword: BookKeyword) -> None:
        pass

    @abstractmethod
    def delete(self, book_keyword: BookKeyword) -> None:
        pass
