from abc import ABCMeta


class ApiException(Exception, metaclass=ABCMeta):
    def __init__(self, *, name: str, message: str, status: int) -> None:
        self.name = name
        self.message = message
        self.status = status

        super().__init__(message)
