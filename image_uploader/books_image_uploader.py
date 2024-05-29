import os
from typing import Any

from flask import current_app
from werkzeug.datastructures import FileStorage

from handle_errors import CustomError

from .image_uploader import ImageUploader


class BooksImageUploader(ImageUploader):
    def __init__(self, image: FileStorage) -> None:
        self._validate_file(image)

        self._file = image
        self._new_filename = self._generate_random_filename()

    def _validate_file(self, file: Any) -> None:
        if not self._is_file_valid(file):
            raise CustomError('InvalidDataSent')

    def _is_file_valid(self, file: FileStorage) -> bool:
        max_size = current_app.config['BOOK_PHOTOS_MAX_SIZE']

        file.stream.seek(0, 2)
        file_size = file.stream.tell()
        file.stream.seek(0)

        return self._has_allowed_extensions(file.filename) and file_size <= max_size

    def get_url(self) -> str:
        return f'{self._base_url}/books/photos/{self._new_filename}'

    def save(self) -> None:
        filename = os.path.join(current_app.config['BOOK_PHOTOS_UPLOAD_DIR'], self._new_filename)
        self._file.save(filename)

    @classmethod
    def delete(cls, img_url: str) -> None:
        filename = os.path.basename(img_url)
        file_path = os.path.join(current_app.config['BOOK_PHOTOS_UPLOAD_DIR'], filename)

        if os.path.exists(file_path):
            os.remove(file_path)
