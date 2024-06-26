import os

from flask import current_app
from injector import inject

from dto.input import BookImgInputDTO
from exception import BookImgException, ImageException
from image_uploader import BookImageUploader
from model import Book, BookImg
from repository import IBookImgRepository, IBookRepository

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
        book_img = BookImg(input_dto.img.get_url())
        book_img.id_book = book.id

        self.book_img_repository.add(book_img)

        input_dto.img.save()

        return book_img

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

        self._swap_book_img(book_img, input_dto.img)

        self.book_img_repository.update()

        return book_img

    def _swap_book_img(self, old_img: BookImg, new_img: BookImageUploader) -> None:
        BookImageUploader.delete(old_img.img_url)

        old_img.update_img_url(new_img.get_url())

        new_img.save()
