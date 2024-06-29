from .base import ApiException


class SavedBookException:
    class BookArentSaved(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'The book {id} was not saved by the user',
                status=404,
            )

    class BookAlreadySaved(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'The book {id} is already saved by the user',
                status=409,
            )
