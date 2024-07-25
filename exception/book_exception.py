from .base import ApiException, ValidationException


class BookException:
    class BookAlreadyExists(ApiException):
        def __init__(self, name: str) -> None:
            super().__init__(
                message=f'The book "{name.strip().title()}" already exists',
                status=409,
            )

    class BookDoesntExist(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                message=f'The book {id} does not exist',
                status=404,
            )

    class BookImageListTooShort(ValidationException):
        def __init__(self, min_qty: int) -> None:
            super().__init__(f'Book must contains at least {min_qty} image')

    class BookImageListTooLong(ValidationException):
        def __init__(self, max_qty: int) -> None:
            super().__init__(f'Book must contains at most {max_qty} images')
