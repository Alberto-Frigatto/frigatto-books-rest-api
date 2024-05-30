from .base import ApiException


class GeneralException:
    class DatabaseConnection(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='Não foi possível se conectar ao banco de dados',
                status=500,
            )

    class MethodNotAllowed(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='Método HTTP não permitido',
                status=405,
            )

    class InvalidContentType(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='Cabeçalho Content-Type inválido',
                status=415,
            )

    class NoDataSent(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='Não foi enviado nenhum dado',
                status=400,
            )

    class InvalidDataSent(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='Os dados enviados são inválidos',
                status=400,
            )
