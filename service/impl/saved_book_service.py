from flask_jwt_extended import current_user
from flask_sqlalchemy.pagination import Pagination
from injector import inject

from model import Book, SavedBook
from repository import IBookRepository, ISavedBookRepository

from .. import ISavedBookService


@inject
class SavedBookService(ISavedBookService):
    def __init__(
        self, book_repository: IBookRepository, saved_book_repository: ISavedBookRepository
    ) -> None:
        self.book_repository = book_repository
        self.saved_book_repository = saved_book_repository

    def get_all_saved_books(self, page: int) -> Pagination:
        return self.saved_book_repository.get_all(page)

    def save_book(self, id: str) -> Book:
        book = self.book_repository.get_by_id(id)
        saved_book = SavedBook(current_user.id, book)

        self.saved_book_repository.add(saved_book)

        return book

    def delete_saved_book(self, id_book: str) -> None:
        book = self.book_repository.get_by_id(id_book)
        saved_book = self.saved_book_repository.get_by_id_book(str(book.id))

        self.saved_book_repository.delete(saved_book)
