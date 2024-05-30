from .base import ApiException


class BookImgException:
    class BookImgDoesntExists(ApiException):
        def __init__(self, id: int) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'A imagem {id} não existe',
                status=404,
            )

    class BookDoesntOwnThisImg(ApiException):
        def __init__(self, id_img: int, id_book: int) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'A imagem {id_img} não pertence ao livro {id_book}',
                status=401,
            )

    class BookMustHaveAtLeastOneImg(ApiException):
        def __init__(self, id_book: int) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'O livro {id_book} deve ter pelo menos uma imagem',
                status=400,
            )
