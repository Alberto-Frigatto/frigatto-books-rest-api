from flask import current_app
from werkzeug.datastructures import FileStorage

from .base import ImageValidator


class BookImageValidator(ImageValidator):
    @classmethod
    def has_valid_size(cls, file: FileStorage) -> bool:
        file_size = cls._get_file_size(file)

        return file_size <= current_app.config['BOOK_PHOTOS_MAX_SIZE']
