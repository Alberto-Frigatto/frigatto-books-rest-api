from injector import inject

from dto.input import BookKeywordInputDTO
from model import BookKeyword
from service import IBookKeywordService

from .. import IBookKeywordController


@inject
class BookKeywordController(IBookKeywordController):
    def __init__(self, service: IBookKeywordService) -> None:
        self.service = service

    def create_book_keyword(self, id_book: str, input_dto: BookKeywordInputDTO) -> BookKeyword:
        return self.service.create_book_keyword(id_book, input_dto)

    def delete_book_keyword(self, id_book: str, id_keyword: str) -> None:
        self.service.delete_book_keyword(id_book, id_keyword)
