from .base import ApiException


class BookKindException:
    class BookKindAlreadyExists(ApiException):
        def __init__(self, kind: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'O tipo de livro "{kind}" já existe',
                status=409,
            )

    class BookKindDoesntExists(ApiException):
        def __init__(self, id: int) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'O tipo de livro {id} não existe',
                status=404,
            )

    class ThereAreLinkedBooksWithThisBookKind(ApiException):
        def __init__(self, id: int) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'O tipo de livro {id} não pode ser excluído, pois há livros desse tipo',
                status=409,
            )
