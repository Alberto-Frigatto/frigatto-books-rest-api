import re
from typing import Any

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db import db, int_pk


class BookKind(db.Model):
    __tablename__ = 'book_kinds'

    id: Mapped[int_pk]
    kind: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    def __init__(self, kind: str) -> None:
        self.kind = kind

    def update_kind(self, kind: str) -> None:
        self.kind = kind
