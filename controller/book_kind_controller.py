from typing import Sequence

from dto.input import BookKindInputDTO
from model import BookKind
from repository import BookKindRepository


class BookKindController:
    repository = BookKindRepository()

    def get_all_book_kinds(self) -> Sequence[BookKind]:
        return self.repository.get_all()

    def get_book_kind_by_id(self, id: str) -> BookKind:
        return self.repository.get_by_id(id)

    def create_book_kind(self, input_dto: BookKindInputDTO) -> BookKind:
        new_book_kind = BookKind(input_dto.kind)

        self.repository.add(new_book_kind)

        return new_book_kind

    def delete_book_kind(self, id: str) -> None:
        self.repository.delete(id)

    def update_book_kind(self, id: str, input_dto: BookKindInputDTO) -> BookKind:
        book_kind = self.repository.get_by_id(id)
        book_kind.update_kind(input_dto.kind)

        self.repository.update(book_kind)

        return book_kind
