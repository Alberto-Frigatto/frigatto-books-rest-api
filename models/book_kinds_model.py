import re
from typing import Any

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db import db
from handle_errors import CustomError


class BookKind(db.Model):
    __tablename__ = 'book_kinds'

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    def __init__(self, kind: str) -> None:
        self._validate_kind_name(kind)
        self.kind = kind

    def _validate_kind_name(self, kind: Any) -> None:
        if not self._is_kind_name_valid(kind):
            raise CustomError('InvalidKindBookName')

    def _is_kind_name_valid(self, kind: Any) -> bool:
        return (
            isinstance(kind, str)
            and len(kind) <= 30
            and re.match(r'^[a-zA-ZáàãâäéèẽêëíìîĩïóòõôöúùũûüÁÀÃÂÄÉÈẼÊËÍÌÎĨÏÓÒÕÔÖÚÙŨÛÜ\s]+$', kind)
        )
