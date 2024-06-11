from .base import ApiException


class BookException:
    class BookAlreadyExists(ApiException):
        def __init__(self, name: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'O livro "{name}" já existe',
                status=409,
            )

    class BookDoesntExists(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'O livro {id} não existe',
                status=404,
            )
