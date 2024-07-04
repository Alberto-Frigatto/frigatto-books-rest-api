from typing import Any


class ApiException(Exception):
    def __init__(self, *, message: Any, status: int) -> None:
        self.name = self.__class__.__name__
        self.message = message
        self.status = status

        super().__init__()
