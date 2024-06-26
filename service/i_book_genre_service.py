from abc import ABC, abstractmethod
from typing import Sequence

from dto.input import BookGenreInputDTO
from model import BookGenre


class IBookGenreService(ABC):
    @abstractmethod
    def get_all_book_genres(self) -> Sequence[BookGenre]:
        pass

    @abstractmethod
    def get_book_genre_by_id(self, id: str) -> BookGenre:
        pass

    @abstractmethod
    def create_book_genre(self, input_dto: BookGenreInputDTO) -> BookGenre:
        pass

    @abstractmethod
    def delete_book_genre(self, id: str) -> None:
        pass

    @abstractmethod
    def update_book_genre(self, id: str, input_dto: BookGenreInputDTO) -> BookGenre:
        pass
