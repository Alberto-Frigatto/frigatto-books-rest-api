from typing import Sequence

from injector import inject

from model import Book
from service import ISavedBookService

from .. import ISavedBookController


@inject
class SavedBookController(ISavedBookController):
    def __init__(self, service: ISavedBookService) -> None:
        self.service = service

    def get_all_saved_books(self) -> Sequence[Book]:
        return self.service.get_all_saved_books()

    def save_book(self, id: str) -> Book:
        return self.service.save_book(id)

    def delete_saved_book(self, id_book: str) -> None:
        self.service.delete_saved_book(id_book)
