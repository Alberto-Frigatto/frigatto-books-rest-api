import os

from flask import current_app, request

from db import db
from handle_errors import CustomError
from image_uploader import BookImageUploader
from model import Book, BookImg

from .controller import Controller

file_path = str
mimetype = str


class BookImgController(Controller):
    def get_book_photo(self, filename: str) -> tuple[file_path, mimetype]:
        if not self._is_file_name_valid(filename):
            raise CustomError('ImageNotFound')

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
            raise CustomError('BookDoesntOwnThisImg')

        if self._does_book_have_one_img(book):
            raise CustomError('BookMustHaveAtLeastOneImg')

        BookImageUploader.delete(book_img.img_url)

        db.session.delete(book_img)
        db.session.commit()

    def _get_book_by_id(self, id: str) -> Book:
        book = db.session.get(Book, id)

        if book is None:
            raise CustomError('BookDoesntExists')

        return book

    def _does_book_have_one_img(self, book: Book) -> bool:
        return len(book.book_imgs) == 1

    def _get_book_img_by_id(self, id: str) -> BookImg:
        book_img = db.session.get(BookImg, id)

        if book_img is None:
            raise CustomError('BookImgDoesntExists')

        return book_img

    def update_book_img(self, id_book: str, id_img: str) -> BookImg:
        if not super().are_there_data():
            raise CustomError('NoDataSent')

        files_data = request.files.to_dict()

        if not self._is_data_valid(files_data):
            raise CustomError('InvalidDataSent')

        book = self._get_book_by_id(id_book)
        book_img = self._get_book_img_by_id(id_img)

        if book_img.id_book != book.id:
            raise CustomError('BookDoesntOwnThisImg')

        image_uploader = BookImageUploader(files_data['img'])

        BookImageUploader.delete(book_img.img_url)

        book_img.update_img_url(image_uploader.get_url())

        image_uploader.save()

        db.session.commit()

        return book_img

    def _is_data_valid(self, files_data: dict) -> bool:
        return 'img' in files_data.keys()

    def create_book_img(self, id_book: str) -> BookImg:
        if not super().are_there_data():
            raise CustomError('NoDataSent')

        files_data = request.files.to_dict()

        if not self._is_data_valid(files_data):
            raise CustomError('InvalidDataSent')

        image_uploader = BookImageUploader(files_data['img'])

        book = self._get_book_by_id(id_book)
        book_img = BookImg(image_uploader.get_url())

        book.book_imgs.append(book_img)

        image_uploader.save()

        db.session.commit()

        return book_img
