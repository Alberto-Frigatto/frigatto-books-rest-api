import os

from flask import current_app, request
from sqlalchemy import select

from db import db
from handle_errors import CustomError
from image_uploaders import BooksImageUploader
from models import BookImg

from .controller import Controller

file_path = str
mimetype = str


class BookImgsController(Controller):
    def get_book_photo(self, filename: str) -> tuple[file_path, mimetype]:
        if not self._is_file_name_valid(filename):
            raise CustomError('ImageNotFound')

        return os.path.join(current_app.config['USER_PHOTOS_UPLOAD_DIR'], filename), 'image/jpeg'

    def _is_file_name_valid(self, filename: str) -> bool:
        return (
            isinstance(filename, str)
            and filename.endswith('.jpg')
            and os.path.isfile(os.path.join(current_app.config['USER_PHOTOS_UPLOAD_DIR'], filename))
        )

    def delete_book_img(self, id_book: int, id_img: int) -> None:
        book_img = self._get_book_img_by_id(id_img)

        if book_img.id_book != id_book:
            raise CustomError('BookDoesntOwnThisImg')

        db.session.delete(book_img)
        db.session.commit()

    def _get_book_img_by_id(self, id_img: int) -> BookImg:
        query = select(BookImg).filter_by(id=id_img)
        book_img = db.session.execute(query).scalar()

        if book_img is None:
            raise CustomError('BookImgDoesntExists')

        return book_img

    def update_book_img(self, id_book: int, id_img: int) -> BookImg:
        if not super()._are_there_data():
            raise CustomError('NoDataSent')

        files_data = request.files.to_dict()

        if not self._is_data_valid_for_update(files_data):
            raise CustomError('InvalidDataSent')

        book_img = self._get_book_img_by_id(id_img)

        if book_img.id_book != id_book:
            raise CustomError('BookDoesntOwnThisImg')

        image_uploader = BooksImageUploader(files_data['img'])

        BooksImageUploader.delete(book_img.img_url)

        book_img.update_img_url(image_uploader.get_url())

        image_uploader.save()

        db.session.commit()

        return book_img

    def _is_data_valid_for_update(self, files_data: dict) -> bool:
        return 'img' in files_data.keys()
