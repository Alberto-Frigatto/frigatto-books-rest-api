from .base import ApiException


class SavedBookException:
    class BookArentSaved(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'O livro {id} não foi salvo pelo usuário',
                status=404,
            )

    class BookAlreadySaved(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'O livro {id} já está salvo pelo usuário',
                status=409,
            )
