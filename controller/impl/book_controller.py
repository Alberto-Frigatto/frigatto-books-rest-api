from flask_sqlalchemy.pagination import Pagination
from injector import inject

from dto.input import CreateBookInputDTO, UpdateBookInputDTO
from model import Book
from service import IBookService

from .. import IBookController


@inject
class BookController(IBookController):
    def __init__(self, service: IBookService) -> None:
        self.service = service

    def get_all_books(self, page: int) -> Pagination:
        return self.service.get_all_books(page)

    def get_book_by_id(self, id: str) -> Book:
        return self.service.get_book_by_id(id)

    def create_book(self, input_dto: CreateBookInputDTO) -> Book:
        return self.service.create_book(input_dto)

    def delete_book(self, id: str) -> None:
        self.service.delete_book(id)

    def update_book(self, id: str, input_dto: UpdateBookInputDTO) -> Book:
        return self.service.update_book(id, input_dto)
