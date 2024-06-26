from typing import Sequence

from injector import inject

from dto.input import BookGenreInputDTO
from model import BookGenre
from service import IBookGenreService

from .. import IBookGenreController


@inject
class BookGenreController(IBookGenreController):
    def __init__(self, service: IBookGenreService) -> None:
        self.service = service

    def get_all_book_genres(self) -> Sequence[BookGenre]:
        return self.service.get_all_book_genres()

    def get_book_genre_by_id(self, id: str) -> BookGenre:
        return self.service.get_book_genre_by_id(id)

    def create_book_genre(self, input_dto: BookGenreInputDTO) -> BookGenre:
        return self.service.create_book_genre(input_dto)

    def delete_book_genre(self, id: str) -> None:
        self.service.delete_book_genre(id)

    def update_book_genre(self, id: str, input_dto: BookGenreInputDTO) -> BookGenre:
        return self.service.update_book_genre(id, input_dto)
