import datetime
import re
from typing import Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db, int_pk
from handle_errors import CustomError
from model import BookGenre, BookImg, BookKeyword, BookKind


class Book(db.Model):
    __tablename__ = 'books'

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    price: Mapped[float] = mapped_column(DECIMAL(6, 2), nullable=False)
    author: Mapped[str] = mapped_column(String(40), nullable=False)
    release_year: Mapped[int] = mapped_column(nullable=False)

    id_kind: Mapped[int] = mapped_column(
        ForeignKey("book_kinds.id", ondelete="restrict"),
        nullable=False,
    )
    id_genre: Mapped[int] = mapped_column(
        ForeignKey("book_genres.id", ondelete="restrict"),
        nullable=False,
    )

    book_genre: Mapped[BookGenre] = relationship()
    book_kind: Mapped[BookKind] = relationship()
    book_keywords: Mapped[list[BookKeyword]] = relationship(cascade='all, delete, delete-orphan')
    book_imgs: Mapped[list[BookImg]] = relationship(cascade='all, delete, delete-orphan')

    def __init__(self, name: str, price: str, author: str, release_year: str) -> None:
        self._validate_name(name)
        self._validate_price(price)
        self._validate_author(author)
        self._validate_release_year(release_year)

        self.name = self._format_text(name)
        self.price = float(price)
        self.author = self._format_text(author)
        self.release_year = int(release_year)

    def _validate_name(self, name: Any) -> None:
        if not self._is_name_valid(name):
            raise CustomError('InvalidDataSent')

    def _is_name_valid(self, name: Any) -> bool:
        if not isinstance(name, str):
            return False

        min_length, max_length = 2, 80
        name_length = len(name)

        return (
            name_length >= min_length
            and name_length <= max_length
            and re.match(
                r'^[a-zA-ZáàãâäéèẽêëíìîĩïóòõôöúùũûüÁÀÃÂÄÉÈẼÊËÍÌÎĨÏÓÒÕÔÖÚÙŨÛÜç\s\d-]+$', name
            )
        )

    def _validate_price(self, price: Any) -> None:
        if not self._is_price_valid(price):
            raise CustomError('InvalidDataSent')

    def _is_price_valid(self, price: Any) -> bool:
        try:
            float_price = float(price)
        except Exception:
            return False

        if float_price < 0:
            return False

        PRECISION = 6

        if not self._is_smaller_or_eq_than_the_precision(price, PRECISION):
            return False

        SCALE = 2

        DECIMAL_SEP = '.'

        pos_decimal_sep = price.find(DECIMAL_SEP)

        if pos_decimal_sep == -1:
            return True

        qty_decimal_digits = len(price) - pos_decimal_sep - 1

        return self._is_smaller_or_eq_than_the_scale(qty_decimal_digits, SCALE)

    def _is_smaller_or_eq_than_the_precision(self, number: str, precision: int) -> bool:
        return len(number.replace('.', '')) <= precision

    def _is_smaller_or_eq_than_the_scale(self, qty_decimal_digits: int, scale: int) -> bool:
        return qty_decimal_digits <= scale

    def _validate_author(self, author: Any) -> None:
        if not self._is_author_valid(author):
            raise CustomError('InvalidDataSent')

    def _is_author_valid(self, author: Any) -> bool:
        if not isinstance(author, str):
            return False

        min_length, max_length = 3, 40
        author_length = len(author)

        return (
            author_length >= min_length
            and author_length <= max_length
            and re.match(
                r'^[a-zA-ZáàãâäéèẽêëíìîĩïóòõôöúùũûüÁÀÃÂÄÉÈẼÊËÍÌÎĨÏÓÒÕÔÖÚÙŨÛÜç\s]+$', author
            )
        )

    def _validate_release_year(self, release_year: Any) -> None:
        if not self._is_release_year_valid(release_year):
            raise CustomError('InvalidDataSent')

    def _is_release_year_valid(self, release_year: Any) -> bool:
        try:
            int_release_year = int(release_year)
        except Exception:
            return False

        min_year, max_year = 1000, datetime.datetime.now().year

        return int_release_year >= min_year and int_release_year <= max_year

    def _format_text(self, text: str) -> str:
        return text.strip()

    def update_name(self, name: str) -> None:
        self._validate_name(name)

        self.name = self._format_text(name)

    def update_price(self, price: str) -> None:
        self._validate_price(price)

        self.price = float(price)

    def update_author(self, author: str) -> None:
        self._validate_author(author)

        self.author = self._format_text(author)

    def update_release_year(self, release_year: str) -> None:
        self._validate_release_year(release_year)

        self.release_year = int(release_year)
