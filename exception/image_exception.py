from .base import ApiException


class ImageException:
    class ImageNotFound(ApiException):
        def __init__(self, filename: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'A imagem {filename} não encontrada',
                status=404,
            )
