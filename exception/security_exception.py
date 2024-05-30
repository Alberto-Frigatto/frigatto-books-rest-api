from .base import ApiException


class SecurityException:
    class InvalidJWT(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='Token JWT inválido',
                status=401,
            )

    class MissingJWT(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='O token JWT não foi enviado',
                status=401,
            )

    class MissingCSFR(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='O token CSFR não foi enviado',
                status=400,
            )

    class InvalidCSFR(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='Token CSFR inválido',
                status=400,
            )
