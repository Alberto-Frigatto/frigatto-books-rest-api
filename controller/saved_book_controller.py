from typing import Sequence

from flask_jwt_extended import current_user
from sqlalchemy import select

from db import db
from exception import BookException, SavedBookException
from model import Book, SavedBook

from .controller import Controller


class SavedBookController(Controller):
    def get_all_saved_books(self) -> Sequence[Book]:
        query = select(SavedBook).filter_by(id_user=current_user.id).order_by(SavedBook.id)
        saved_books = db.session.execute(query).scalars().all()

        return [saved_book.book for saved_book in saved_books]

    def save_book(self, id: str) -> Book:
        saved_books = self.get_all_saved_books()
        book = self._get_book_by_id(id)

        if book in saved_books:
            raise SavedBookException.BookAlreadySaved(id)

        saved_book = SavedBook(current_user.id, book)

        db.session.add(saved_book)
        db.session.commit()

        return book

    def _get_book_by_id(self, id: str) -> Book:
        book = db.session.get(Book, id)

        if book is None:
            raise BookException.BookDoesntExists(id)

        return book

    def delete_saved_book(self, id_book: str) -> None:
        saved_books = self.get_all_saved_books()
        book = self._get_book_by_id(id_book)

        if book not in saved_books:
            raise SavedBookException.BookArentSaved(id_book)

        db.session.delete(book)
        db.session.commit()
