from .base import ApiException


class BookException:
    class BookAlreadyExists(ApiException):
        def __init__(self, name: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'The book "{name}" already exists',
                status=409,
            )

    class BookDoesntExists(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'The book {id} does not exist',
                status=404,
            )
