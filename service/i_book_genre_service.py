from abc import ABC, abstractmethod

from flask_sqlalchemy.pagination import Pagination

from dto.input import BookGenreInputDTO
from model import BookGenre


class IBookGenreService(ABC):
    @abstractmethod
    def get_all_book_genres(self, page: int) -> Pagination:
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
