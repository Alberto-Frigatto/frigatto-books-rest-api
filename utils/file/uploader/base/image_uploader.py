import uuid
from abc import ABCMeta, abstractmethod

from werkzeug.datastructures import FileStorage


class ImageUploader(metaclass=ABCMeta):
    _base_url = 'http://localhost:5000'

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
    @abstractmethod
    def delete(cls, img_url: str) -> None:
        pass

    @property
    def file(self) -> FileStorage:
        return self._file
