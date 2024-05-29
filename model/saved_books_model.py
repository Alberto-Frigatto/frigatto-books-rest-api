from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db, int_pk
from model import Book


class SavedBook(db.Model):
    __tablename__ = 'saved_books'

    id: Mapped[int_pk]
    id_user: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"),
        nullable=False,
    )
    id_book: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="cascade"),
        nullable=False,
    )

    book: Mapped[Book] = relationship()

    def __init__(self, id_user: int, book: Book) -> None:
        self.id_user = id_user
        self.book = book
