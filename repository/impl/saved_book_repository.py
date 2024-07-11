from flask_jwt_extended import current_user
from flask_sqlalchemy.pagination import Pagination
from injector import inject
from sqlalchemy import select

from db import IDbSession
from exception import SavedBookException
from model import Book, SavedBook

from .. import ISavedBookRepository


@inject
class SavedBookRepository(ISavedBookRepository):
    def __init__(self, session: IDbSession) -> None:
        self.session = session

    def get_all(self, page: int) -> Pagination:
        query = select(SavedBook).filter_by(id_user=current_user.id).order_by(SavedBook.id)
        pagination = self.session.paginate(query, page=page)
        pagination.items = [saved_book.book for saved_book in pagination.items]

        return pagination

    def add(self, saved_book: SavedBook) -> None:
        if self._saved_book_already_exists(saved_book.book):
            raise SavedBookException.BookAlreadySaved(str(saved_book.book.id))

        self.session.add(saved_book)

    def _saved_book_already_exists(self, saved_book: Book) -> bool:
        query = select(SavedBook).filter_by(id_user=current_user.id)

        return saved_book in [saved_book.book for saved_book in self.session.get_many(query)]

    def delete(self, saved_book: SavedBook) -> None:
        self.session.delete(saved_book)

    def get_by_id_book(self, id_book: str) -> SavedBook:
        query = select(SavedBook).filter_by(id_book=id_book, id_user=current_user.id)
        saved_book = self.session.get_one(query)

        if saved_book is None:
            raise SavedBookException.BookIsNotSaved(str(id_book))

        return saved_book
