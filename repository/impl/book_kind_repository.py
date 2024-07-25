from flask_sqlalchemy.pagination import Pagination
from injector import inject
from sqlalchemy import select

from db import IDbSession
from exception import BookKindException
from model import Book, BookKind

from .. import IBookKindRepository


@inject
class BookKindRepository(IBookKindRepository):
    def __init__(self, session: IDbSession) -> None:
        self.session = session

    def get_all(self, page: int) -> Pagination:
        query = select(BookKind).order_by(BookKind.id)

        return self.session.paginate(query, page=page)

    def get_by_id(self, id: str) -> BookKind:
        book_kind = self.session.get_by_id(BookKind, id)

        if book_kind is None:
            raise BookKindException.BookKindDoesntExist(str(id))

        return book_kind

    def add(self, book_kind: BookKind) -> None:
        if self._book_kind_already_exists(book_kind):
            raise BookKindException.BookKindAlreadyExists(book_kind.kind)

        self.session.add(book_kind)

    def _book_kind_already_exists(self, book_kind: BookKind) -> bool:
        query = select(BookKind).filter_by(kind=book_kind.kind).where((BookKind.id != book_kind.id))

        return bool(self.session.get_one(query))

    def delete(self, id: str) -> None:
        book_kind = self.get_by_id(id)

        if self._are_there_linked_books(book_kind):
            raise BookKindException.ThereAreLinkedBooksWithThisBookKind(id)

        self.session.delete(book_kind)

    def _are_there_linked_books(self, book_kind: BookKind) -> bool:
        query = select(Book).filter_by(id_kind=book_kind.id)
        return bool(self.session.get_many(query))

    def update(self, book_kind: BookKind) -> None:
        if self._book_kind_already_exists(book_kind):
            raise BookKindException.BookKindAlreadyExists(book_kind.kind)

        self.session.update()
