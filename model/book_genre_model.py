from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db import int_pk

from .base import Model


class BookGenre(Model):
    __tablename__ = 'book_genres'

    id: Mapped[int_pk]
    genre: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    def __init__(self, genre: str) -> None:
        self.genre = genre

    def update_genre(self, genre: str) -> None:
        self.genre = genre
