from abc import ABC, abstractmethod

from flask_sqlalchemy.pagination import Pagination

from dto.input import BookKindInputDTO
from model import BookKind


class IBookKindService(ABC):
    @abstractmethod
    def get_all_book_kinds(self, page: int) -> Pagination:
        pass

    @abstractmethod
    def get_book_kind_by_id(self, id: str) -> BookKind:
        pass

    @abstractmethod
    def create_book_kind(self, input_dto: BookKindInputDTO) -> BookKind:
        pass

    @abstractmethod
    def delete_book_kind(self, id: str) -> None:
        pass

    @abstractmethod
    def update_book_kind(self, id: str, input_dto: BookKindInputDTO) -> BookKind:
        pass
