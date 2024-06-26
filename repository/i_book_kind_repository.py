from abc import ABC, abstractmethod
from typing import Sequence

from model import BookKind


class IBookKindRepository(ABC):
    @abstractmethod
    def get_all(self) -> Sequence[BookKind]:
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> BookKind:
        pass

    @abstractmethod
    def add(self, book_kind: BookKind) -> None:
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        pass

    @abstractmethod
    def update(self, book_kind: BookKind) -> None:
        pass
