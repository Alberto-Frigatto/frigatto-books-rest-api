from .base import ApiException


class BookKindException:
    class BookKindAlreadyExists(ApiException):
        def __init__(self, kind: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'The book kind "{kind}" already exists',
                status=409,
            )

    class BookKindDoesntExists(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'The book kind {id} does not exist',
                status=404,
            )

    class ThereAreLinkedBooksWithThisBookKind(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'The book genre {id} cannot be deleted because there are books linked to this kind',
                status=409,
            )
