from typing import Any, Sequence

from sqlalchemy import select

from db import db
from exception import BookKindException, GeneralException
from model import Book, BookKind

from .controller import Controller


class BookKindController(Controller):
    def get_all_book_kinds(self) -> Sequence[BookKind]:
        query = select(BookKind).order_by(BookKind.id)
        book_kinds = db.session.execute(query).scalars().all()

        return book_kinds

    def get_book_kind_by_id(self, id: str) -> BookKind:
        book_kind = db.session.get(BookKind, id)

        if book_kind is None:
            raise BookKindException.BookKindDoesntExists(id)

        return book_kind

    def create_book_kind(self) -> BookKind:
        if not super().are_there_data():
            raise GeneralException.NoDataSent()

        data = super().get_json_data()

        if not self._is_data_valid(data):
            raise GeneralException.InvalidDataSent()

        new_book_kind = BookKind(data['kind'])

        if self._book_kind_already_exists(new_book_kind):
            raise BookKindException.BookKindAlreadyExists(id)

        db.session.add(new_book_kind)
        db.session.commit()

        return new_book_kind

    def _is_data_valid(self, data: Any) -> bool:
        return isinstance(data, dict) and 'kind' in data.keys()

    def _book_kind_already_exists(self, book_kind: BookKind | str) -> bool:
        query = select(BookKind).filter_by(
            kind=(
                book_kind.kind
                if isinstance(book_kind, BookKind)
                else (book_kind.strip().lower() if isinstance(book_kind, str) else book_kind)
            )
        )
        return bool(db.session.execute(query).scalar())

    def delete_book_kind(self, id: str) -> None:
        book_kind = self.get_book_kind_by_id(id)

        if self._are_there_linked_books(book_kind):
            raise BookKindException.ThereAreLinkedBooksWithThisBookKind(id)

        db.session.delete(book_kind)
        db.session.commit()

    def _are_there_linked_books(self, book_kind: BookKind) -> bool:
        query = select(Book).filter_by(id_kind=book_kind.id)
        return bool(db.session.execute(query).scalars().all())

    def update_book_kind(self, id: str) -> BookKind:
        book_kind = self.get_book_kind_by_id(id)

        if not super().are_there_data():
            raise GeneralException.NoDataSent()

        data = super().get_json_data()

        if not self._is_data_valid(data):
            raise GeneralException.InvalidDataSent()

        new_kind = data['kind']

        if self._book_kind_already_exists(new_kind):
            raise BookKindException.BookKindAlreadyExists(new_kind)

        book_kind.update_kind(new_kind)
        db.session.commit()

        return book_kind
