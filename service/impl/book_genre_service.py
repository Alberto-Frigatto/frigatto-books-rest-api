from typing import Sequence

from injector import inject

from dto.input import BookGenreInputDTO
from model import BookGenre
from repository import IBookGenreRepository

from .. import IBookGenreService


@inject
class BookGenreService(IBookGenreService):
    def __init__(self, repository: IBookGenreRepository) -> None:
        self.repository = repository

    def get_all_book_genres(self) -> Sequence[BookGenre]:
        return self.repository.get_all()

    def get_book_genre_by_id(self, id: str) -> BookGenre:
        return self.repository.get_by_id(id)

    def create_book_genre(self, input_dto: BookGenreInputDTO) -> BookGenre:
        new_book_genre = BookGenre(input_dto.genre)

        self.repository.add(new_book_genre)

        return new_book_genre

    def delete_book_genre(self, id: str) -> None:
        self.repository.delete(id)

    def update_book_genre(self, id: str, input_dto: BookGenreInputDTO) -> BookGenre:
        book_genre = self.repository.get_by_id(id)
        book_genre.update_genre(input_dto.genre)

        self.repository.update(book_genre)

        return book_genre
