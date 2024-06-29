from .base import ApiException


class BookKeywordException:
    class BookKeywordDoesntExists(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'The keyword {id} does not exist',
                status=404,
            )

    class BookDoesntOwnThisKeyword(ApiException):
        def __init__(self, id_keyword: str, id_book: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'The keyword {id_keyword} does not belong to the book {id_book}',
                status=401,
            )

    class BookMustHaveAtLeastOneKeyword(ApiException):
        def __init__(self, id_book: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'The book {id_book} must have at least one keyword',
                status=400,
            )
