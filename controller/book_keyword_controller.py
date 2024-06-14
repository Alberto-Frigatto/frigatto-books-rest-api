from dto.input import CreateBookKeywordDTO
from exception import BookKeywordException
from model import Book, BookKeyword
from repository import BookKeywordRepository, BookRepository


class BookKeywordController:
    book_keyword_repository = BookKeywordRepository()
    book_repository = BookRepository()

    def create_book_keyword(self, id_book: str, input_dto: CreateBookKeywordDTO) -> BookKeyword:
        book = self.book_repository.get_by_id(id_book)
        book_keyword = BookKeyword(input_dto.keyword)
        book_keyword.id_book = book.id

        self.book_keyword_repository.add(book_keyword)

        return book_keyword

    def delete_book_keyword(self, id_book: str, id_keyword: str) -> None:
        book = self.book_repository.get_by_id(id_book)

        book_keyword = self.book_keyword_repository.get_by_id(id_keyword)

        if book_keyword.id_book != book.id:
            raise BookKeywordException.BookDoesntOwnThisKeyword(id_keyword, id_book)

        if self._does_book_have_one_keyword(book):
            raise BookKeywordException.BookMustHaveAtLeastOneKeyword(id_book)

        self.book_keyword_repository.delete(book_keyword)

    def _does_book_have_one_keyword(self, book: Book) -> bool:
        return len(book.book_keywords) == 1
