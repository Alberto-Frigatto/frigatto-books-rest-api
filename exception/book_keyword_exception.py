from .base import ApiException


class BookKeywordException:
    class BookKeywordDoesntExists(ApiException):
        def __init__(self, id: int) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'A palavra chave {id} não existe',
                status=404,
            )

    class BookDoesntOwnThisKeyword(ApiException):
        def __init__(self, id_keyword: int, id_book: int) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'A palavra chave {id_keyword} não pertence ao livro {id_book}',
                status=401,
            )

    class BookMustHaveAtLeastOneKeyword(ApiException):
        def __init__(self, id_book: int) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'O livro {id_book} deve ter pelo menos uma palavra chave',
                status=400,
            )
