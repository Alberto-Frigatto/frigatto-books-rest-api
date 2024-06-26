from typing import Sequence

from injector import inject

from dto.input import BookKindInputDTO
from model import BookKind
from service import IBookKindService

from .. import IBookKindController


@inject
class BookKindController(IBookKindController):
    def __init__(self, service: IBookKindService) -> None:
        self.service = service

    def get_all_book_kinds(self) -> Sequence[BookKind]:
        return self.service.get_all_book_kinds()

    def get_book_kind_by_id(self, id: str) -> BookKind:
        return self.service.get_book_kind_by_id(id)

    def create_book_kind(self, input_dto: BookKindInputDTO) -> BookKind:
        return self.service.create_book_kind(input_dto)

    def delete_book_kind(self, id: str) -> None:
        self.service.delete_book_kind(id)

    def update_book_kind(self, id: str, input_dto: BookKindInputDTO) -> BookKind:
        return self.service.update_book_kind(id, input_dto)
