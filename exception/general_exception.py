from typing import Any

from .base import ApiException


class GeneralException:
    class DatabaseConnection(ApiException):
        def __init__(self) -> None:
            super().__init__(
                message='Unable to connect to the database',
                status=500,
            )

    class MethodNotAllowed(ApiException):
        def __init__(self) -> None:
            super().__init__(
                message='HTTP method not allowed',
                status=405,
            )

    class InvalidContentType(ApiException):
        def __init__(self) -> None:
            super().__init__(
                message='Invalid Content-Type header',
                status=415,
            )

    class NoDataSent(ApiException):
        def __init__(self) -> None:
            super().__init__(
                message='No data sent',
                status=400,
            )

    class InvalidDataSent(ApiException):
        def __init__(self, detail: Any | None = None) -> None:
            super().__init__(
                message='Invalid data sent',
                status=400,
                detail=detail,
            )

    class EnpointNotFound(ApiException):
        def __init__(self) -> None:
            super().__init__(
                message='The endpoint does not exist',
                status=400,
            )

    class PaginationPageDoesNotExists(ApiException):
        def __init__(self, page: int) -> None:
            super().__init__(
                message=f'The page {page} does not exist',
                status=400,
            )
