from .base import ApiException, ValidationException


class BookKeywordException:
    class BookKeywordDoesntExist(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                message=f'The keyword {id} does not exist',
                status=404,
            )

    class BookDoesntOwnThisKeyword(ApiException):
        def __init__(self, id_keyword: str, id_book: str) -> None:
            super().__init__(
                message=f'The keyword {id_keyword} does not belong to the book {id_book}',
                status=403,
            )

    class BookMustHaveAtLeastOneKeyword(ApiException):
        def __init__(self, id_book: str) -> None:
            super().__init__(
                message=f'The book {id_book} must have at least one keyword',
                status=400,
            )

    class BookMustContainsAtLeastOneKeywordOnCreation(ValidationException):
        def __init__(self) -> None:
            super().__init__('Book must contains at least 1 keyword')
