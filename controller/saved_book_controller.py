from flask_jwt_extended import current_user

from model import Book, SavedBook
from repository import BookRepository, SavedBookRepository


class SavedBookController:
    saved_book_repository = SavedBookRepository()
    book_repository = BookRepository()

    def get_all_saved_books(self) -> list[Book]:
        return self.saved_book_repository.get_all()

    def save_book(self, id: str) -> Book:
        book = self.book_repository.get_by_id(id)
        saved_book = SavedBook(current_user.id, book)

        self.saved_book_repository.add(saved_book)

        return book

    def delete_saved_book(self, id_book: str) -> None:
        book = self.book_repository.get_by_id(id_book)
        saved_book = self.saved_book_repository.get_by_id_book(book.id)
        self.saved_book_repository.delete(saved_book)
