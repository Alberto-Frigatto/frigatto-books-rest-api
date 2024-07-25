from .base import ApiException


class SavedBookException:
    class BookIsNotSaved(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                message=f'The book {id} was not saved by the user',
                status=404,
            )

    class BookAlreadySaved(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                message=f'The book {id} is already saved by the user',
                status=409,
            )
