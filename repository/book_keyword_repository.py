from db import db
from exception import BookKeywordException
from model import BookKeyword


class BookKeywordRepository:
    def get_by_id(self, id: str) -> BookKeyword:
        book_keyword = db.session.get(BookKeyword, id)

        if book_keyword is None:
            raise BookKeywordException.BookKeywordDoesntExists(id)

        return book_keyword

    def add(self, new_book_keyword: BookKeyword) -> None:
        db.session.add(new_book_keyword)
        db.session.commit()

    def delete(self, book_keyword: BookKeyword) -> None:
        db.session.delete(book_keyword)
        db.session.commit()
