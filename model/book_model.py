import datetime
import re
from typing import Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db, int_pk
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

    def __init__(self, name: str, price: float, author: str, release_year: int) -> None:
        self.name = name
        self.price = price
        self.author = author
        self.release_year = release_year

    def update_name(self, name: str) -> None:
        self.name = name

    def update_price(self, price: float) -> None:
        self.price = price

    def update_author(self, author: str) -> None:
        self.author = author

    def update_release_year(self, release_year: int) -> None:
        self.release_year = release_year
