from abc import ABC, abstractmethod

from dto.input import BookImgInputDTO
from model import BookImg

file_path = str
mimetype = str


class IBookImgController(ABC):
    @abstractmethod
    def get_book_photo(self, filename: str) -> tuple[file_path, mimetype]:
        pass

    @abstractmethod
    def create_book_img(self, id_book: str, input_dto: BookImgInputDTO) -> BookImg:
        pass

    @abstractmethod
    def delete_book_img(self, id_book: str, id_img: str) -> None:
        pass

    @abstractmethod
    def update_book_img(self, id_book: str, id_img: str, input_dto: BookImgInputDTO) -> BookImg:
        pass
