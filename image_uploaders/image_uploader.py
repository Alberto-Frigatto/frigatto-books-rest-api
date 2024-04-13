import uuid
from abc import ABCMeta, abstractmethod

from werkzeug.datastructures import FileStorage


class ImageUploader(metaclass=ABCMeta):
    _base_url = 'http://localhost:5000'

    @abstractmethod
    def __init__(self, image: FileStorage) -> None:
        pass

    @abstractmethod
    def _is_file_valid(self) -> bool:
        pass

    @abstractmethod
    def get_url(self) -> bool:
        pass

    @abstractmethod
    def save(self) -> None:
        pass

    def _generate_random_filename(self) -> str:
        return str(uuid.uuid4()).replace('-', '') + '.jpg'

    @abstractmethod
    @classmethod
    def delete(cls, img_url: str) -> None:
        pass
