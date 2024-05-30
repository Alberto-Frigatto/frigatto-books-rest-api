import re
from typing import Any

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db import db, int_pk
from exception import GeneralException


class BookGenre(db.Model):
    __tablename__ = 'book_genres'

    id: Mapped[int_pk]
    genre: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    def __init__(self, genre: str) -> None:
        self._validate_genre_name(genre)
        self.genre = self._format_genre(genre)

    def _validate_genre_name(self, genre: Any) -> None:
        if not self._is_genre_name_valid(genre):
            raise GeneralException.InvalidDataSent()

    def _is_genre_name_valid(self, genre: Any) -> bool:
        if not isinstance(genre, str):
            return False

        min_length, max_length = 3, 30
        genre_length = len(genre)

        return (
            genre_length >= min_length
            and genre_length <= max_length
            and re.match(r'^[a-zA-ZáàãâäéèẽêëíìîĩïóòõôöúùũûüÁÀÃÂÄÉÈẼÊËÍÌÎĨÏÓÒÕÔÖÚÙŨÛÜç\s]+$', genre)
        )

    def _format_genre(self, genre: str) -> str:
        return genre.strip().lower()

    def update_genre(self, genre: str) -> None:
        self._validate_genre_name(genre)

        self.genre = self._format_genre(genre)
