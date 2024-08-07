import os

from flask import current_app

from .base import ImageUploader


class BookImageUploader(ImageUploader):
    def get_url(self) -> str:
        return f'{super()._base_url}/books/photos/{self._new_filename}'

    def save(self) -> None:
        filename = os.path.join(current_app.config['BOOK_PHOTOS_UPLOAD_DIR'], self._new_filename)
        self._file.save(filename)

    @classmethod
    def delete(cls, img_url: str) -> None:
        filename = os.path.basename(img_url)
        file_path = os.path.join(current_app.config['BOOK_PHOTOS_UPLOAD_DIR'], filename)

        if os.path.exists(file_path):
            os.remove(file_path)
