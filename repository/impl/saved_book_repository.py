from typing import Sequence

from flask_jwt_extended import current_user
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

    def get_all(self) -> list[Book]:
        query = select(SavedBook).filter_by(id_user=current_user.id).order_by(SavedBook.id)
        saved_books: Sequence[SavedBook] = self.session.get_many(query)

        return [saved_book.book for saved_book in saved_books]

    def add(self, saved_book: SavedBook) -> None:
        if self._saved_book_already_exists(saved_book.book):
            raise SavedBookException.BookAlreadySaved(str(saved_book.book.id))

        self.session.add(saved_book)

    def _saved_book_already_exists(self, saved_book: Book) -> bool:
        return saved_book in self.get_all()

    def delete(self, saved_book: SavedBook) -> None:
        self.session.delete(saved_book)

    def get_by_id_book(self, id_book: str) -> SavedBook:
        query = select(SavedBook).filter_by(id_book=id_book, id_user=current_user.id)
        saved_book = self.session.get_one(query)

        if saved_book is None:
            raise SavedBookException.BookArentSaved(str(id_book))

        return saved_book
