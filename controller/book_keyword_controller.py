from typing import Any

from db import db
from exception import BookException, BookKeywordException, GeneralException
from model import Book, BookKeyword

from .controller import Controller


class BookKeywordController(Controller):
    def create_book_keyword(self, id_book: str) -> BookKeyword:
        if not super().are_there_data():
            raise GeneralException.NoDataSent()

        data = super().get_json_data()

        if not self._is_data_valid(data):
            raise GeneralException.InvalidDataSent()

        book = self._get_book_by_id(id_book)
        book_keyword = BookKeyword(data['keyword'])

        book.book_keywords.append(book_keyword)

        db.session.commit()

        return book_keyword

    def _is_data_valid(self, data: Any) -> bool:
        return isinstance(data, dict) and 'keyword' in data.keys()

    def _get_book_by_id(self, id: str) -> Book:
        book = db.session.get(Book, id)

        if book is None:
            raise BookException.BookDoesntExists(id)

        return book

    def delete_book_keyword(self, id_book: str, id_keyword: str) -> None:
        book = self._get_book_by_id(id_book)

        book_keyword = self._get_book_keyword_by_id(id_keyword)

        if book_keyword.id_book != book.id:
            raise BookKeywordException.BookDoesntOwnThisKeyword(id_keyword, id_book)

        if self._does_book_have_one_keyword(book):
            raise BookKeywordException.BookMustHaveAtLeastOneKeyword(id_book)

        db.session.delete(book_keyword)
        db.session.commit()

    def _get_book_keyword_by_id(self, id: str) -> BookKeyword:
        book = db.session.get(BookKeyword, id)

        if book is None:
            raise BookKeywordException.BookKeywordDoesntExists(id)

        return book

    def _does_book_have_one_keyword(self, book: Book) -> bool:
        return len(book.book_keywords) == 1
