import os

from flask import current_app
from injector import inject

from dto.input import BookImgInputDTO
from exception import BookImgException, ImageException
from model import Book, BookImg
from repository import IBookImgRepository, IBookRepository
from utils.file.uploader import BookImageUploader

from .. import IBookImgService

file_path = str
mimetype = str


@inject
class BookImgService(IBookImgService):
    def __init__(
        self, book_repository: IBookRepository, book_img_repository: IBookImgRepository
    ) -> None:
        self.book_repository = book_repository
        self.book_img_repository = book_img_repository

    def get_book_photo(self, filename: str) -> tuple[file_path, mimetype]:
        if not self._is_file_name_valid(filename):
            raise ImageException.ImageNotFound(filename)

        return os.path.join(current_app.config['BOOK_PHOTOS_UPLOAD_DIR'], filename), 'image/jpeg'

    def _is_file_name_valid(self, filename: str) -> bool:
        return (
            isinstance(filename, str)
            and filename.endswith('.jpg')
            and os.path.isfile(os.path.join(current_app.config['BOOK_PHOTOS_UPLOAD_DIR'], filename))
        )

    def create_book_img(self, id_book: str, input_dto: BookImgInputDTO) -> BookImg:
        book = self.book_repository.get_by_id(id_book)

        if self._does_book_already_have_max_qty_imgs(book):
            raise BookImgException.BookAlreadyHaveImageMaxQty(book.name)

        book_img = BookImg(input_dto.img.get_url())
        book_img.id_book = book.id

        self.book_img_repository.add(book_img)
        input_dto.img.save()

        return book_img

    def _does_book_already_have_max_qty_imgs(self, book: Book) -> bool:
        return len(book.book_imgs) == current_app.config['BOOK_IMG_MAX_QTY']

    def delete_book_img(self, id_book: str, id_img: str) -> None:
        book = self.book_repository.get_by_id(id_book)
        book_img = self.book_img_repository.get_by_id(id_img)

        if book_img.id_book != book.id:
            raise BookImgException.BookDoesntOwnThisImg(id_img, id_book)

        if self._does_book_have_one_img(book):
            raise BookImgException.BookMustHaveAtLeastOneImg(id_book)

        self.book_img_repository.delete(book_img)

    def _does_book_have_one_img(self, book: Book) -> bool:
        return len(book.book_imgs) == 1

    def update_book_img(self, id_book: str, id_img: str, input_dto: BookImgInputDTO) -> BookImg:
        book = self.book_repository.get_by_id(id_book)
        book_img = self.book_img_repository.get_by_id(id_img)

        if book_img.id_book != book.id:
            raise BookImgException.BookDoesntOwnThisImg(id_img, id_book)

        old_img_url = book_img.img_url
        book_img.update_img_url(input_dto.img.get_url())

        self.book_img_repository.update()

        BookImageUploader.delete(old_img_url)
        input_dto.img.save()

        return book_img
