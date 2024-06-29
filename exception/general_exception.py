from typing import Any

from .base import ApiException


class GeneralException:
    class DatabaseConnection(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='Unable to connect to the database',
                status=500,
            )

    class MethodNotAllowed(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='HTTP method not allowed',
                status=405,
            )

    class InvalidContentType(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='Invalid Content-Type header',
                status=415,
            )

    class NoDataSent(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='No data sent',
                status=400,
            )

    class InvalidDataSent(ApiException):
        def __init__(self, message: Any = 'Invalid data sent') -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=message,
                status=400,
            )

    class EnpointNotFound(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='The endpoint does not exist',
                status=400,
            )

    class PaginationPageDoesNotExists(ApiException):
        def __init__(self, page: int) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'The page {page} does not exist',
                status=400,
            )
