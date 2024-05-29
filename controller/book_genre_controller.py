from typing import Any, Sequence

from sqlalchemy import select

from db import db
from handle_errors import CustomError
from model import Book, BookGenre

from .controller import Controller


class BookGenreController(Controller):
    def get_all_book_genres(self) -> Sequence[BookGenre]:
        query = select(BookGenre).order_by(BookGenre.id)
        book_genres = db.session.execute(query).scalars().all()

        return book_genres

    def get_book_genre_by_id(self, id: str) -> BookGenre:
        book_genre = db.session.get(BookGenre, id)

        if book_genre is None:
            raise CustomError('BookGenreDoesntExists')

        return book_genre

    def create_book_genre(self) -> BookGenre:
        if not super().are_there_data():
            raise CustomError('NoDataSent')

        data = super().get_json_data()

        if not self._is_data_valid(data):
            raise CustomError('InvalidDataSent')

        new_book_genre = BookGenre(data['genre'])

        if self._book_genre_already_exists(new_book_genre):
            raise CustomError('BookGenreAlreadyExists')

        db.session.add(new_book_genre)
        db.session.commit()

        return new_book_genre

    def _is_data_valid(self, data: Any) -> bool:
        return isinstance(data, dict) and 'genre' in data.keys()

    def _book_genre_already_exists(self, book_genre: BookGenre | str) -> bool:
        query = select(BookGenre).filter_by(
            genre=(
                book_genre.genre
                if isinstance(book_genre, BookGenre)
                else (book_genre.strip().lower() if isinstance(book_genre, str) else book_genre)
            )
        )

        return bool(db.session.execute(query).scalar())

    def delete_book_genre(self, id: str) -> None:
        book_genre = self.get_book_genre_by_id(id)

        if self._are_there_linked_books(book_genre):
            raise CustomError('ThereAreLinkedBooksWithThisBookGenre')

        db.session.delete(book_genre)
        db.session.commit()

    def _are_there_linked_books(self, book_genre: BookGenre) -> bool:
        query = select(Book).filter_by(id_genre=book_genre.id)
        return bool(db.session.execute(query).scalars().all())

    def update_book_genre(self, id: str) -> BookGenre:
        book_genre = self.get_book_genre_by_id(id)

        if not super().are_there_data():
            raise CustomError('NoDataSent')

        data = super().get_json_data()

        if not self._is_data_valid(data):
            raise CustomError('InvalidDataSent')

        if self._book_genre_already_exists(data['genre']):
            raise CustomError('BookGenreAlreadyExists')

        book_genre.update_genre(data['genre'])
        db.session.commit()

        return book_genre
