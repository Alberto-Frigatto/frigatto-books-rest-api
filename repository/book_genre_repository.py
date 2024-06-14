from typing import Sequence

from sqlalchemy import select

from db import db
from exception import BookGenreException
from model import Book, BookGenre


class BookGenreRepository:
    def get_all(self) -> Sequence[BookGenre]:
        query = select(BookGenre).order_by(BookGenre.id)

        return db.session.execute(query).scalars().all()

    def get_by_id(self, id: str | int) -> BookGenre:
        book_genre = db.session.get(BookGenre, id)

        if book_genre is None:
            raise BookGenreException.BookGenreDoesntExists(str(id))

        return book_genre

    def add(self, new_book_genre: BookGenre) -> None:
        if self._book_genre_already_exists(new_book_genre.genre):
            raise BookGenreException.BookGenreAlreadyExists(new_book_genre.genre)

        db.session.add(new_book_genre)
        db.session.commit()

    def _book_genre_already_exists(self, book_genre_name: str) -> bool:
        with db.session.no_autoflush:
            query = select(BookGenre).filter_by(genre=book_genre_name)

            return bool(db.session.execute(query).scalar())

    def delete(self, id: str) -> None:
        book_genre = self.get_by_id(id)

        if self._are_there_linked_books(book_genre):
            raise BookGenreException.ThereAreLinkedBooksWithThisBookGenre(id)

        db.session.delete(book_genre)
        db.session.commit()

    def _are_there_linked_books(self, book_genre: BookGenre) -> bool:
        query = select(Book).filter_by(id_genre=book_genre.id)
        return bool(db.session.execute(query).scalars().all())

    def update(self, updated_book_genre: BookGenre) -> None:
        if self._book_genre_already_exists(updated_book_genre.genre):
            raise BookGenreException.BookGenreAlreadyExists(updated_book_genre.genre)

        db.session.commit()
