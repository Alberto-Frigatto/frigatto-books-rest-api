from abc import ABCMeta
from typing import Any


class ApiException(Exception, metaclass=ABCMeta):
    def __init__(self, *, name: str, message: str | Any, status: int) -> None:
        self.name = name
        self.message = message
        self.status = status

        super().__init__(message)
