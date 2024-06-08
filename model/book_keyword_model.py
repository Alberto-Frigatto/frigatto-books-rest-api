from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from db import db, int_pk


class BookKeyword(db.Model):
    __tablename__ = 'book_keywords'

    id: Mapped[int_pk]
    keyword: Mapped[str] = mapped_column(String(20), nullable=False)

    id_book: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), nullable=False)

    def __init__(self, keyword: str) -> None:
        self.keyword = keyword
