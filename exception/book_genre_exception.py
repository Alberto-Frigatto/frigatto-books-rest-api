from .base import ApiException


class BookGenreException:
    class BookGenreAlreadyExists(ApiException):
        def __init__(self, genre: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'The book genre "{genre}" already exists',
                status=409,
            )

    class BookGenreDoesntExists(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'The book genre {id} does not exist',
                status=404,
            )

    class ThereAreLinkedBooksWithThisBookGenre(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'The book genre {id} cannot be deleted because there are books linked to this genre',
                status=409,
            )
