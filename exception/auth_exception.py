from .base import ApiException


class AuthException:
    class InvalidLogin(ApiException):
        def __init__(self) -> None:
            super().__init__(
                message='Invalid username or password',
                status=401,
            )

    class UserAlreadyAuthenticated(ApiException):
        def __init__(self) -> None:
            super().__init__(
                message='The user is already logged in',
                status=400,
            )
