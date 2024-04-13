import re
from typing import Any

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db import db, int_pk
from handle_errors import CustomError


class BookKind(db.Model):
    __tablename__ = 'book_kinds'

    id: Mapped[int_pk]
    kind: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    def __init__(self, kind: str) -> None:
        self._validate_kind_name(kind)
        self.kind = self._format_kind_name(kind)

    def _validate_kind_name(self, kind: Any) -> None:
        if not self._is_kind_name_valid(kind):
            raise CustomError('InvalidDataSent')

    def _is_kind_name_valid(self, kind: Any) -> bool:
        return (
            isinstance(kind, str)
            and kind
            and len(kind) <= 30
            and re.match(r'^[a-zA-ZáàãâäéèẽêëíìîĩïóòõôöúùũûüÁÀÃÂÄÉÈẼÊËÍÌÎĨÏÓÒÕÔÖÚÙŨÛÜç\s]+$', kind)
        )

    def _format_kind_name(self, kind: str) -> str:
        return kind.strip().lower()

    def update_kind(self, kind: str) -> None:
        self._validate_kind_name(kind)

        self.kind = self._format_kind_name(kind)
