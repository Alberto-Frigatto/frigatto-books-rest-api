from typing import Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from db import db, int_pk


class BookImg(db.Model):
    __tablename__ = 'book_imgs'

    id: Mapped[int_pk]
    img_url: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    id_book: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )

    def __init__(self, img_url: str) -> None:
        self.img_url = img_url

    def update_img_url(self, img_url: str) -> None:
        self.img_url = img_url
