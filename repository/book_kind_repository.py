from typing import Sequence

from injector import inject
from sqlalchemy import select
from sqlalchemy.orm import scoped_session

from exception import BookKindException
from model import Book, BookKind


@inject
class BookKindRepository:
    def __init__(self, session: scoped_session) -> None:
        self.session = session

    def get_all(self) -> Sequence[BookKind]:
        query = select(BookKind).order_by(BookKind.id)

        return self.session.execute(query).scalars().all()

    def get_by_id(self, id: str | int) -> BookKind:
        book_kind = self.session.get(BookKind, id)

        if book_kind is None:
            raise BookKindException.BookKindDoesntExists(str(id))

        return book_kind

    def add(self, new_book_kind: BookKind) -> None:
        if self._book_kind_already_exists(new_book_kind.kind):
            raise BookKindException.BookKindAlreadyExists(new_book_kind.kind)

        self.session.add(new_book_kind)
        self.session.commit()

    def _book_kind_already_exists(self, book_kind_name: str) -> bool:
        with self.session.no_autoflush:
            query = select(BookKind).filter_by(kind=book_kind_name)

            return bool(self.session.execute(query).scalar())

    def delete(self, id: str) -> None:
        book_kind = self.get_by_id(id)

        if self._are_there_linked_books(book_kind):
            raise BookKindException.ThereAreLinkedBooksWithThisBookKind(id)

        self.session.delete(book_kind)
        self.session.commit()

    def _are_there_linked_books(self, book_kind: BookKind) -> bool:
        query = select(Book).filter_by(id_kind=book_kind.id)
        return bool(self.session.execute(query).scalars().all())

    def update(self, updated_book_kind: BookKind) -> None:
        if self._book_kind_already_exists(updated_book_kind.kind):
            raise BookKindException.BookKindAlreadyExists(updated_book_kind.kind)

        self.session.commit()
