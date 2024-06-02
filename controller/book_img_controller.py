import os

from flask import current_app, request

from db import db
from dto.input import CreateBookImgDTO, UpdateBookImgDTO
from exception import BookException, BookImgException, GeneralException, ImageException
from image_uploader import BookImageUploader
from model import Book, BookImg

from .controller import Controller

file_path = str
mimetype = str


class BookImgController(Controller):
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

    def delete_book_img(self, id_book: str, id_img: str) -> None:
        book = self._get_book_by_id(id_book)

        book_img = self._get_book_img_by_id(id_img)

        if book_img.id_book != book.id:
            raise BookImgException.BookDoesntOwnThisImg(id_img, id_book)

        if self._does_book_have_one_img(book):
            raise BookImgException.BookMustHaveAtLeastOneImg(id_book)

        BookImageUploader.delete(book_img.img_url)

        db.session.delete(book_img)
        db.session.commit()

    def _get_book_by_id(self, id: str) -> Book:
        book = db.session.get(Book, id)

        if book is None:
            raise BookException.BookDoesntExists(id)

        return book

    def _does_book_have_one_img(self, book: Book) -> bool:
        return len(book.book_imgs) == 1

    def _get_book_img_by_id(self, id: str) -> BookImg:
        book_img = db.session.get(BookImg, id)

        if book_img is None:
            raise BookImgException.BookImgDoesntExists(id)

        return book_img

    def update_book_img(self, *, id_book: str, id_img: str, input_dto: UpdateBookImgDTO) -> BookImg:
        book = self._get_book_by_id(id_book)
        book_img = self._get_book_img_by_id(id_img)

        if book_img.id_book != book.id:
            raise BookImgException.BookDoesntOwnThisImg(id_img, id_book)

        self._swap_book_img(book_img, input_dto.img)

        db.session.commit()

        return book_img

    def _swap_book_img(self, old_img: BookImg, new_img: BookImageUploader) -> None:
        BookImageUploader.delete(old_img.img_url)

        old_img.update_img_url(new_img.get_url())

        new_img.save()

    def create_book_img(self, id_book: str, input_dto: CreateBookImgDTO) -> BookImg:
        book = self._get_book_by_id(id_book)
        book_img = BookImg(input_dto.img.get_url())

        book.book_imgs.append(book_img)

        input_dto.img.save()

        db.session.commit()

        return book_img
