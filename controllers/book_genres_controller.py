from typing import Any, Sequence

from flask import request
from sqlalchemy import select

from db import db
from handle_errors import CustomError
from models import BookGenre


class BookGenresController:
    def get_all_book_genres(self) -> Sequence[BookGenre]:
        book_genres = db.session.execute(select(BookGenre).order_by(BookGenre.id)).scalars().all()

        return book_genres

    def get_book_genre_by_id(self, id: int) -> BookGenre:
        book_genre = db.session.execute(select(BookGenre).filter_by(id=id)).scalar()

        if book_genre is None:
            raise CustomError('BookGenreDoesntExists')

        return book_genre

    def create_book_genre(self) -> BookGenre:
        if not self._are_there_data():
            raise CustomError('NoDataSent')

        data = request.json

        if not self._is_data_valid(data):
            raise CustomError('InvalidDataSent')

        new_book_genre = BookGenre(data['genre'])

        if self._book_genre_already_exists(new_book_genre):
            raise CustomError('BookGenreAlreadyExists')

        db.session.add(new_book_genre)
        db.session.commit()

        return new_book_genre

    def _are_there_data(self) -> bool:
        return request.content_length

    def _is_data_valid(self, data: Any) -> bool:
        return isinstance(data, dict) and 'genre' in data.keys() and isinstance(data['genre'], str)

    def _book_genre_already_exists(self, book_genre: BookGenre) -> bool:
        return bool(
            db.session.execute(select(BookGenre).filter_by(genre=book_genre.genre)).scalar()
        )

    def delete_book_genre(self, id: int) -> None:
        book_genre = self.get_book_genre_by_id(id)

        db.session.delete(book_genre)
        db.session.commit()

    def update_book_genre(self, id: int) -> BookGenre:
        book_genre = self.get_book_genre_by_id(id)

        if not self._are_there_data():
            raise CustomError('NoDataSent')

        data = request.json

        if not self._is_data_valid(data):
            raise CustomError('InvalidDataSent')

        book_genre.update_genre(data['genre'])
        db.session.commit()

        return book_genre