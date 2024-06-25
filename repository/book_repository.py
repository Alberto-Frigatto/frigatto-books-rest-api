from typing import Sequence

from injector import inject
from sqlalchemy import select
from sqlalchemy.orm import scoped_session

from exception import BookException
from image_uploader import BookImageUploader
from model import Book


@inject
class BookRepository:
    def __init__(self, session: scoped_session) -> None:
        self.session = session

    def get_all(self) -> Sequence[Book]:
        query = select(Book).order_by(Book.id)

        return self.session.execute(query).scalars().all()

    def get_by_id(self, id: str | int) -> Book:
        book = self.session.get(Book, id)

        if book is None:
            raise BookException.BookDoesntExists(str(id))

        return book

    def add(self, new_book: Book) -> None:
        if self._book_already_exists(new_book.name):
            raise BookException.BookAlreadyExists(new_book.name)

        self.session.add(new_book)
        self.session.commit()

    def _book_already_exists(self, name: str) -> bool:
        with self.session.no_autoflush:
            query = select(Book).where(Book.name.ilike(name))

            return bool(self.session.execute(query).scalar())

    def delete(self, id: str) -> None:
        book = self.get_by_id(id)

        for book_img in book.book_imgs:
            BookImageUploader.delete(book_img.img_url)

        self.session.delete(book)
        self.session.commit()

    def update(self, updated_book: Book) -> None:
        if self._was_name_modified(updated_book) and self._book_already_exists(updated_book.name):
            raise BookException.BookAlreadyExists(updated_book.name)

        self.session.commit()

    def _was_name_modified(self, updated_book: Book) -> bool:
        with self.session.no_autoflush:
            query = select(Book.name).filter_by(id=updated_book.id)
            old_name = self.session.execute(query).scalar()

            return updated_book.name != old_name
