from .base import ApiException


class BookGenreException:
    class BookGenreAlreadyExists(ApiException):
        def __init__(self, genre: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'O gênero de livro "{genre}" já existe',
                status=409,
            )

    class BookGenreDoesntExists(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'O gênero de livro {id} não existe',
                status=404,
            )

    class ThereAreLinkedBooksWithThisBookGenre(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message=f'O gênero de livro {id} não pode ser excluído, pois há livros desse gênero',
                status=409,
            )
