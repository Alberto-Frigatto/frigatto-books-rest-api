from flask_sqlalchemy.pagination import Pagination
from injector import inject
from sqlalchemy import select

from db import IDbSession
from exception import BookException
from image_uploader import BookImageUploader
from model import Book

from .. import IBookRepository


@inject
class BookRepository(IBookRepository):
    def __init__(self, session: IDbSession) -> None:
        self.session = session

    def get_all(self, page: int) -> Pagination:
        query = select(Book).order_by(Book.id)

        return self.session.paginate(query, page=page)

    def get_by_id(self, id: str) -> Book:
        book = self.session.get_by_id(Book, id)

        if book is None:
            raise BookException.BookDoesntExists(str(id))

        return book

    def add(self, book: Book) -> None:
        if self._book_already_exists(book.name):
            raise BookException.BookAlreadyExists(book.name)

        self.session.add(book)

    def _book_already_exists(self, name: str) -> bool:
        query = select(Book).where(Book.name.ilike(name))

        return bool(self.session.get_one(query))

    def delete(self, id: str) -> None:
        book = self.get_by_id(id)

        for book_img in book.book_imgs:
            BookImageUploader.delete(book_img.img_url)

        self.session.delete(book)

    def update(self, book: Book) -> None:
        if self._was_name_modified(book) and self._book_already_exists(book.name):
            raise BookException.BookAlreadyExists(book.name)

        self.session.update()

    def _was_name_modified(self, updated_book: Book) -> bool:
        query = select(Book.name).filter_by(id=updated_book.id)
        old_name = self.session.get_one(query)

        return updated_book.name != old_name
