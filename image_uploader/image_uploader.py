import uuid
from abc import ABCMeta, abstractmethod

from werkzeug.datastructures import FileStorage


class ImageUploader(metaclass=ABCMeta):
    _base_url = 'http://localhost:5000'
    _allowed_extensions = '.png', '.jpg', '.jpeg'

    def __init__(self, image: FileStorage) -> None:
        self._file = image
        self._new_filename = self._generate_random_filename()

    def _generate_random_filename(self) -> str:
        return f'{str(uuid.uuid4()).replace("-", "")}.jpg'

    @abstractmethod
    def get_url(self) -> str:
        pass

    @abstractmethod
    def save(self) -> None:
        pass

    @classmethod
    def _has_valid_extensions(cls, filename: str | None) -> bool:
        return isinstance(filename, str) and filename.lower().endswith(cls._allowed_extensions)

    @classmethod
    def _get_file_size(cls, file: FileStorage) -> int:
        file.stream.seek(0, 2)
        file_size = file.stream.tell()
        file.stream.seek(0)

        return file_size

    @classmethod
    @abstractmethod
    def delete(cls, img_url: str) -> None:
        pass
