from typing import Sequence

from sqlalchemy import select

from db import db
from exception import BookKindException
from model import Book, BookKind


class BookKindRepository:
    def get_all(self) -> Sequence[BookKind]:
        query = select(BookKind).order_by(BookKind.id)

        return db.session.execute(query).scalars().all()

    def get_by_id(self, id: str | int) -> BookKind:
        book_kind = db.session.get(BookKind, id)

        if book_kind is None:
            raise BookKindException.BookKindDoesntExists(str(id))

        return book_kind

    def add(self, new_book_kind: BookKind) -> None:
        if self._book_kind_already_exists(new_book_kind.kind):
            raise BookKindException.BookKindAlreadyExists(new_book_kind.kind)

        db.session.add(new_book_kind)
        db.session.commit()

    def _book_kind_already_exists(self, book_kind_name: str) -> bool:
        with db.session.no_autoflush:
            query = select(BookKind).filter_by(kind=book_kind_name)

            return bool(db.session.execute(query).scalar())

    def delete(self, id: str) -> None:
        book_kind = self.get_by_id(id)

        if self._are_there_linked_books(book_kind):
            raise BookKindException.ThereAreLinkedBooksWithThisBookKind(id)

        db.session.delete(book_kind)
        db.session.commit()

    def _are_there_linked_books(self, book_kind: BookKind) -> bool:
        query = select(Book).filter_by(id_kind=book_kind.id)
        return bool(db.session.execute(query).scalars().all())

    def update(self, updated_book_kind: BookKind) -> None:
        if self._book_kind_already_exists(updated_book_kind.kind):
            raise BookKindException.BookKindAlreadyExists(updated_book_kind.kind)

        db.session.commit()
