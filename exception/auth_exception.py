from .base import ApiException


class AuthException:
    class InvalidLogin(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='username ou password inválidos',
                status=401,
            )

    class UserAlreadyAuthenticated(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='O usuário já está logado',
                status=400,
            )
