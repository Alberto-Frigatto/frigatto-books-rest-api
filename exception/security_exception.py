from .base import ApiException


class SecurityException:
    class InvalidJWT(ApiException):
        def __init__(self) -> None:
            super().__init__(
                message='Invalid JWT token',
                status=401,
            )

    class MissingJWT(ApiException):
        def __init__(self) -> None:
            super().__init__(
                message='JWT token not provided',
                status=401,
            )

    class MissingCSRF(ApiException):
        def __init__(self) -> None:
            super().__init__(
                message='CSRF token not provided',
                status=400,
            )

    class InvalidCSRF(ApiException):
        def __init__(self) -> None:
            super().__init__(
                message='Invalid CSRF token',
                status=400,
            )
