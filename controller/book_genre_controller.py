from typing import Sequence

from sqlalchemy import select

from db import db
from dto.input import CreateBookGenreDTO, UpdateBookGenreDTO
from exception import BookGenreException
from model import Book, BookGenre


class BookGenreController:
    def get_all_book_genres(self) -> Sequence[BookGenre]:
        query = select(BookGenre).order_by(BookGenre.id)
        book_genres = db.session.execute(query).scalars().all()

        return book_genres

    def get_book_genre_by_id(self, id: str) -> BookGenre:
        book_genre = db.session.get(BookGenre, id)

        if book_genre is None:
            raise BookGenreException.BookGenreDoesntExists(id)

        return book_genre

    def create_book_genre(self, input_dto: CreateBookGenreDTO) -> BookGenre:
        new_book_genre = BookGenre(input_dto.genre)

        if self._book_genre_already_exists(input_dto.genre):
            raise BookGenreException.BookGenreAlreadyExists(input_dto.genre)

        db.session.add(new_book_genre)
        db.session.commit()

        return new_book_genre

    def _book_genre_already_exists(self, book_genre: str) -> bool:
        query = select(BookGenre).filter_by(genre=book_genre)

        return bool(db.session.execute(query).scalar())

    def delete_book_genre(self, id: str) -> None:
        book_genre = self.get_book_genre_by_id(id)

        if self._are_there_linked_books(book_genre):
            raise BookGenreException.ThereAreLinkedBooksWithThisBookGenre(id)

        db.session.delete(book_genre)
        db.session.commit()

    def _are_there_linked_books(self, book_genre: BookGenre) -> bool:
        query = select(Book).filter_by(id_genre=book_genre.id)
        return bool(db.session.execute(query).scalars().all())

    def update_book_genre(self, id: str, input_dto: UpdateBookGenreDTO) -> BookGenre:
        book_genre = self.get_book_genre_by_id(id)
        new_genre = input_dto.genre

        if self._book_genre_already_exists(new_genre):
            raise BookGenreException.BookGenreAlreadyExists(new_genre)

        book_genre.update_genre(new_genre)
        db.session.commit()

        return book_genre
