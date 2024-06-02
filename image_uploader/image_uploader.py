import uuid
from abc import ABCMeta, abstractmethod

from werkzeug.datastructures import FileStorage


class ImageUploader(metaclass=ABCMeta):
    _base_url = 'http://localhost:5000'
    _allowed_extensions = '.png', '.jpg', '.jpeg'

    @abstractmethod
    def __init__(self, image: FileStorage) -> None:
        pass

    @abstractmethod
    def get_url(self) -> bool:
        pass

    @abstractmethod
    def save(self) -> None:
        pass

    def _generate_random_filename(self) -> str:
        return f'{str(uuid.uuid4()).replace("-", "")}.jpg'

    def _has_allowed_extensions(self, filename: str) -> bool:
        return filename.lower().endswith(self._allowed_extensions)

    @classmethod
    @abstractmethod
    def delete(cls, img_url: str) -> None:
        pass
