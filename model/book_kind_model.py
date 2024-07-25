from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db import int_pk

from .base import Model


class BookKind(Model):
    __tablename__ = 'book_kinds'

    id: Mapped[int_pk]
    kind: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    def __init__(self, kind: str) -> None:
        self.kind = kind

    def update_kind(self, kind: str) -> None:
        self.kind = kind
