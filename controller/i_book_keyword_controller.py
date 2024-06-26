from abc import ABC, abstractmethod

from dto.input import BookKeywordInputDTO
from model import BookKeyword


class IBookKeywordController(ABC):
    @abstractmethod
    def create_book_keyword(self, id_book: str, input_dto: BookKeywordInputDTO) -> BookKeyword:
        pass

    @abstractmethod
    def delete_book_keyword(self, id_book: str, id_keyword: str) -> None:
        pass
