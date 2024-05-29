import re
from typing import Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from db import db, int_pk
from handle_errors import CustomError


class BookKeyword(db.Model):
    __tablename__ = 'book_keywords'

    id: Mapped[int_pk]
    keyword: Mapped[str] = mapped_column(String(20), nullable=False)

    id_book: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), nullable=False)

    def __init__(self, keyword: str) -> None:
        self._validate_keyword(keyword)
        self.keyword = self._format_keyword(keyword)

    def _validate_keyword(self, keyword: Any) -> None:
        if not self._is_keyword_valid(keyword):
            raise CustomError('InvalidDataSent')

    def _is_keyword_valid(self, keyword: Any) -> bool:
        if not isinstance(keyword, str):
            return False

        min_length, max_length = 3, 20
        keyword_length = len(keyword)

        return (
            keyword_length >= min_length
            and keyword_length <= max_length
            and re.match(
                r'^[a-zA-ZáàãâäéèẽêëíìîĩïóòõôöúùũûüÁÀÃÂÄÉÈẼÊËÍÌÎĨÏÓÒÕÔÖÚÙŨÛÜç\s\d]+$', keyword
            )
        )

    def _format_keyword(self, keyword: str) -> str:
        return keyword.strip().lower()
