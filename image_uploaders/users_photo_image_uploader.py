import os
from typing import Any

from werkzeug.datastructures import FileStorage

from handle_errors import CustomError

from .image_uploader import ImageUploader


class UsersPhotoImageUploader(ImageUploader):
    _UPLOAD_DIR = 'uploads/users_photos'

    def __init__(self, image: FileStorage) -> None:
        self._validate_file(image)

        self._file = image
        self._new_filename = self._generate_random_filename()

    def _validate_file(self, file: Any) -> None:
        if not self._is_file_valid(file):
            raise CustomError('InvalidUserPhoto')

    def _is_file_valid(self, file: Any) -> bool:
        if not isinstance(file, FileStorage):
            return False

        max_size = 5 * 1024 * 1024

        file.stream.seek(0, 2)
        file_size = file.stream.tell()
        file.stream.seek(0)

        return file.filename.lower().endswith(('.png', '.jpg', '.jpeg')) and file_size <= max_size

    def get_url(self) -> bool:
        return self._base_url + f'/users/photos/{self._new_filename}'

    def save(self) -> None:
        filename = os.path.join(self._UPLOAD_DIR, self._new_filename)
        self._file.save(filename)

    @classmethod
    def delete(cls, img_url: str) -> None:
        filename = os.path.basename(img_url)
        file_path = os.path.join(cls._UPLOAD_DIR, filename)

        if os.path.exists(file_path):
            os.remove(file_path)
