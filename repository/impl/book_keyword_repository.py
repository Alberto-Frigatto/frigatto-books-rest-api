from injector import inject

from db import IDbSession
from exception import BookKeywordException
from model import BookKeyword

from .. import IBookKeywordRepository


@inject
class BookKeywordRepository(IBookKeywordRepository):
    def __init__(self, session: IDbSession) -> None:
        self.session = session

    def get_by_id(self, id: str) -> BookKeyword:
        book_keyword = self.session.get_by_id(BookKeyword, id)

        if book_keyword is None:
            raise BookKeywordException.BookKeywordDoesntExists(id)

        return book_keyword

    def add(self, book_keyword: BookKeyword) -> None:
        self.session.add(book_keyword)

    def delete(self, book_keyword: BookKeyword) -> None:
        self.session.delete(book_keyword)
