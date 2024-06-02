import os

from flask import current_app
from werkzeug.datastructures import FileStorage

from .image_uploader import ImageUploader


class BookImageUploader(ImageUploader):
    def __init__(self, image: FileStorage) -> None:
        self._file = image
        self._new_filename = self._generate_random_filename()

    def get_url(self) -> str:
        return f'{super()._base_url}/books/photos/{self._new_filename}'

    def save(self) -> None:
        filename = os.path.join(current_app.config['BOOK_PHOTOS_UPLOAD_DIR'], self._new_filename)
        self._file.save(filename)

    @classmethod
    def validate_file(cls, file: FileStorage) -> None:
        max_size = current_app.config['BOOK_PHOTOS_MAX_SIZE']

        file.stream.seek(0, 2)
        file_size = file.stream.tell()
        file.stream.seek(0)

        return cls._has_valid_extensions(file.filename) and file_size <= max_size

    @classmethod
    def _has_valid_extensions(cls, filename: str) -> bool:
        return filename.lower().endswith(cls._allowed_extensions)

    @classmethod
    def delete(cls, img_url: str) -> None:
        filename = os.path.basename(img_url)
        file_path = os.path.join(current_app.config['BOOK_PHOTOS_UPLOAD_DIR'], filename)

        if os.path.exists(file_path):
            os.remove(file_path)
