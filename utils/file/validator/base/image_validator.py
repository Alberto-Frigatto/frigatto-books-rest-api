from abc import ABC, abstractmethod
from typing import Any

from werkzeug.datastructures import FileStorage


class ImageValidator(ABC):
    _allowed_extensions = '.png', '.jpg', '.jpeg'

    @classmethod
    def is_a_file(cls, file: Any) -> bool:
        return isinstance(file, FileStorage)

    @classmethod
    def has_valid_extension(cls, file: FileStorage) -> bool:
        filename = file.filename

        return isinstance(filename, str) and filename.lower().endswith(cls._allowed_extensions)

    @classmethod
    @abstractmethod
    def has_valid_size(cls, file: FileStorage) -> bool:
        pass

    @classmethod
    def _get_file_size(cls, file: FileStorage) -> int:
        file.stream.seek(0, 2)
        file_size = file.stream.tell()
        file.stream.seek(0)

        return file_size
