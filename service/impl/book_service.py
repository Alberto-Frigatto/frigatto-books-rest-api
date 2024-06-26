from typing import Any, Sequence

from injector import inject

from dto.input import CreateBookInputDTO, UpdateBookInputDTO
from model import Book, BookImg, BookKeyword
from repository import IBookGenreRepository, IBookKindRepository, IBookRepository

from .. import IBookService


@inject
class BookService(IBookService):
    def __init__(
        self,
        book_repository: IBookRepository,
        book_genre_repository: IBookGenreRepository,
        book_kind_repository: IBookKindRepository,
    ) -> None:
        self.book_repository = book_repository
        self.book_genre_repository = book_genre_repository
        self.book_kind_repository = book_kind_repository

    def get_all_books(self) -> Sequence[Book]:
        return self.book_repository.get_all()

    def get_book_by_id(self, id: str) -> Book:
        return self.book_repository.get_by_id(id)

    def create_book(self, input_dto: CreateBookInputDTO) -> Book:
        new_book = Book(
            input_dto.name,
            input_dto.price,
            input_dto.author,
            input_dto.release_year,
        )

        book_kind = self.book_kind_repository.get_by_id(str(input_dto.id_book_kind))
        book_genre = self.book_genre_repository.get_by_id(str(input_dto.id_book_genre))
        book_keywords = [BookKeyword(keyword) for keyword in input_dto.keywords]
        book_imgs = [BookImg(img.get_url()) for img in input_dto.imgs]

        new_book.book_kind = book_kind
        new_book.book_genre = book_genre
        new_book.book_keywords = book_keywords
        new_book.book_imgs = book_imgs

        self.book_repository.add(new_book)

        for img in input_dto.imgs:
            img.save()

        return new_book

    def delete_book(self, id: str) -> None:
        self.book_repository.delete(id)

    def update_book(self, id: str, input_dto: UpdateBookInputDTO) -> Book:
        book = self.get_book_by_id(id)

        for key, value in input_dto.__dict__.items():
            if value is not None:
                self._update_book_attrs(book, key, value)

        self.book_repository.update(book)

        return book

    def _update_book_attrs(self, book: Book, key: str, value: Any):
        if key not in ('id_book_kind', 'id_book_genre'):
            getattr(book, f'update_{key.strip()}')(value)
        else:
            if key == 'id_book_kind':
                book_kind = self.book_kind_repository.get_by_id(value)
                book.book_kind = book_kind
            else:
                book_genre = self.book_genre_repository.get_by_id(value)
                book.book_genre = book_genre
