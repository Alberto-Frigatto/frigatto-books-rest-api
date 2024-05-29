from typing import Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from db import db, int_pk
from handle_errors import CustomError


class BookImg(db.Model):
    __tablename__ = 'book_imgs'

    id: Mapped[int_pk]
    img_url: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    id_book: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )

    def __init__(self, img_url: str) -> None:
        self._validate_img_url(img_url)
        self.img_url = self._format_img_url(img_url)

    def _validate_img_url(self, img_url: Any) -> None:
        if not self._is_img_url_valid(img_url):
            raise CustomError('InvalidDataSent')

    def _is_img_url_valid(self, img_url: Any) -> bool:
        if not isinstance(img_url, str):
            return False

        min_length, max_length = 5, 255

        img_url_length = len(img_url)

        return img_url_length >= min_length and img_url_length <= max_length

    def _format_img_url(self, img_url: str) -> str:
        return img_url.strip().lower()

    def update_img_url(self, img_url: str) -> None:
        self._validate_img_url(img_url)

        self.img_url = self._format_img_url(img_url)
