from typing import Sequence

from flask_jwt_extended import current_user
from sqlalchemy import select

from db import db
from handle_errors import CustomError
from models import Book, SavedBook

from .controller import Controller


class SavedBooksController(Controller):
    def get_all_saved_books(self) -> Sequence[Book]:
        query = select(SavedBook).filter_by(id_user=current_user.id).order_by(SavedBook.id)
        saved_books = db.session.execute(query).scalars().all()

        return [saved_book.book for saved_book in saved_books]

    def save_book(self, id: int) -> Book:
        saved_books = self.get_all_saved_books()
        book = self._get_book_by_id(id)

        if book in saved_books:
            raise CustomError('BookAlreadySaved')

        saved_book = SavedBook(current_user.id, book)

        db.session.add(saved_book)
        db.session.commit()

        return book

    def _get_book_by_id(self, id: int) -> Book:
        book_kind = db.session.get(Book, id)

        if book_kind is None:
            raise CustomError('BookDoesntExists')

        return book_kind

    def delete_saved_book(self, id_book: int) -> None:
        saved_books = self.get_all_saved_books()
        book = self._get_book_by_id(id_book)

        if book not in saved_books:
            raise CustomError('BookArentSaved')

        saved_book = [book for book in saved_books if book.id == id_book][0]

        db.session.delete(saved_book)
        db.session.commit()
