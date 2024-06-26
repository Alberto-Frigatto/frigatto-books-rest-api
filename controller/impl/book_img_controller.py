from injector import inject

from dto.input import BookImgInputDTO
from model import BookImg
from service import IBookImgService

from .. import IBookImgController

file_path = str
mimetype = str


@inject
class BookImgController(IBookImgController):
    def __init__(self, service: IBookImgService) -> None:
        self.service = service

    def get_book_photo(self, filename: str) -> tuple[file_path, mimetype]:
        return self.service.get_book_photo(filename)

    def create_book_img(self, id_book: str, input_dto: BookImgInputDTO) -> BookImg:
        return self.service.create_book_img(id_book, input_dto)

    def delete_book_img(self, id_book: str, id_img: str) -> None:
        self.service.delete_book_img(id_book, id_img)

    def update_book_img(self, id_book: str, id_img: str, input_dto: BookImgInputDTO) -> BookImg:
        return self.service.update_book_img(id_book, id_img, input_dto)
