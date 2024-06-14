from typing import Sequence

from flask_jwt_extended import current_user
from sqlalchemy import select

from db import db
from exception import SavedBookException
from model import Book, SavedBook


class SavedBookRepository:
    def get_all(self) -> list[Book]:
        query = select(SavedBook).filter_by(id_user=current_user.id).order_by(SavedBook.id)
        saved_books: Sequence[SavedBook] = db.session.execute(query).scalars().all()

        return [saved_book.book for saved_book in saved_books]

    def add(self, new_saved_book: SavedBook) -> None:
        if self._saved_book_already_exists(new_saved_book.book):
            raise SavedBookException.BookAlreadySaved(str(new_saved_book.book.id))

        db.session.add(new_saved_book)
        db.session.commit()

    def _saved_book_already_exists(self, saved_book: Book) -> bool:
        return saved_book in self.get_all()

    def delete(self, saved_book: SavedBook) -> None:
        db.session.delete(saved_book)
        db.session.commit()

    def get_by_id_book(self, id_book: int) -> SavedBook:
        query = select(SavedBook).filter_by(id_book=id_book)
        saved_book = db.session.execute(query).scalar()

        if saved_book is None:
            raise SavedBookException.BookArentSaved(str(id_book))

        return saved_book
