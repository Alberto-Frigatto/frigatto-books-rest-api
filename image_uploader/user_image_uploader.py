import os

from flask import current_app
from werkzeug.datastructures import FileStorage

from .image_uploader import ImageUploader


class UserImageUploader(ImageUploader):
    def get_url(self) -> str:
        return f'{super()._base_url}/users/photos/{self._new_filename}'

    def save(self) -> None:
        filename = os.path.join(current_app.config['USER_PHOTOS_UPLOAD_DIR'], self._new_filename)
        self._file.save(filename)

    @classmethod
    def validate_file(cls, file: FileStorage) -> bool:
        max_size = current_app.config['USER_PHOTOS_MAX_SIZE']
        file_size = cls._get_file_size(file)

        return cls._has_valid_extensions(file.filename) and file_size <= max_size

    @classmethod
    def delete(cls, img_url: str) -> None:
        filename = os.path.basename(img_url)
        file_path = os.path.join(current_app.config['USER_PHOTOS_UPLOAD_DIR'], filename)

        if os.path.exists(file_path):
            os.remove(file_path)
