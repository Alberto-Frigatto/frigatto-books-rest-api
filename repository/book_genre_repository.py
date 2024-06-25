from typing import Sequence

from injector import inject
from sqlalchemy import select
from sqlalchemy.orm import scoped_session

from exception import BookGenreException
from model import Book, BookGenre


@inject
class BookGenreRepository:
    def __init__(self, session: scoped_session) -> None:
        self.session = session

    def get_all(self) -> Sequence[BookGenre]:
        query = select(BookGenre).order_by(BookGenre.id)

        return self.session.execute(query).scalars().all()

    def get_by_id(self, id: str | int) -> BookGenre:
        book_genre = self.session.get(BookGenre, id)

        if book_genre is None:
            raise BookGenreException.BookGenreDoesntExists(str(id))

        return book_genre

    def add(self, new_book_genre: BookGenre) -> None:
        if self._book_genre_already_exists(new_book_genre.genre):
            raise BookGenreException.BookGenreAlreadyExists(new_book_genre.genre)

        self.session.add(new_book_genre)
        self.session.commit()

    def _book_genre_already_exists(self, book_genre_name: str) -> bool:
        with self.session.no_autoflush:
            query = select(BookGenre).filter_by(genre=book_genre_name)

            return bool(self.session.execute(query).scalar())

    def delete(self, id: str) -> None:
        book_genre = self.get_by_id(id)

        if self._are_there_linked_books(book_genre):
            raise BookGenreException.ThereAreLinkedBooksWithThisBookGenre(id)

        self.session.delete(book_genre)
        self.session.commit()

    def _are_there_linked_books(self, book_genre: BookGenre) -> bool:
        query = select(Book).filter_by(id_genre=book_genre.id)
        return bool(self.session.execute(query).scalars().all())

    def update(self, updated_book_genre: BookGenre) -> None:
        if self._book_genre_already_exists(updated_book_genre.genre):
            raise BookGenreException.BookGenreAlreadyExists(updated_book_genre.genre)

        self.session.commit()
