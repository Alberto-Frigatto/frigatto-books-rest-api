import os
from typing import Any, Sequence

from flask import request
from sqlalchemy import select

from db import db
from dto.input import CreateBookDTO, UpdateBookDTO
from exception import BookException, BookGenreException, BookKindException, GeneralException
from image_uploader import BookImageUploader
from model import Book, BookGenre, BookImg, BookKeyword, BookKind

from .controller import Controller

file_path = str
mimetype = str


class BookController(Controller):
    def get_all_books(self) -> Sequence[Book]:
        query = select(Book).order_by(Book.id)
        books = db.session.execute(query).scalars().all()

        return books

    def get_book_by_id(self, id: str) -> Book:
        book = db.session.get(Book, id)

        if book is None:
            raise BookException.BookDoesntExists(id)

        return book

    def create_book(self, input_dto: CreateBookDTO) -> Book:
        name = input_dto.name

        if self._book_already_exists(name):
            raise BookException.BookAlreadyExists(name)

        new_book = Book(
            name,
            input_dto.price,
            input_dto.author,
            input_dto.release_year,
        )

        book_kind = self._get_book_kind_by_id(input_dto.id_book_kind)
        book_genre = self._get_book_genre_by_id(input_dto.id_book_genre)
        book_keywords = [BookKeyword(keyword) for keyword in input_dto.keywords]
        book_imgs = [BookImg(img.get_url()) for img in input_dto.imgs]

        new_book.book_kind = book_kind
        new_book.book_genre = book_genre
        new_book.book_keywords = book_keywords
        new_book.book_imgs = book_imgs

        for img in input_dto.imgs:
            img.save()

        db.session.add(new_book)
        db.session.commit()

        return new_book

    def _book_already_exists(self, name: str) -> bool:
        query = select(Book).where(Book.name.ilike(name))

        return bool(db.session.execute(query).scalar())

    def _get_book_kind_by_id(self, id: str) -> BookKind:
        book_kind = db.session.get(BookKind, id)

        if book_kind is None:
            raise BookKindException.BookKindDoesntExists(id)

        return book_kind

    def _get_book_genre_by_id(self, id: str) -> BookGenre:
        book_genre = db.session.get(BookGenre, id)

        if book_genre is None:
            raise BookGenreException.BookGenreDoesntExists(id)

        return book_genre

    def delete_book(self, id: str) -> None:
        book = self.get_book_by_id(id)

        for book_img in book.book_imgs:
            BookImageUploader.delete(book_img.img_url)

        db.session.delete(book)
        db.session.commit()

    def update_book(self, id: str, input_dto: UpdateBookDTO) -> Book:
        if self._are_there_name_in_request(input_dto.name) and self._book_already_exists(
            input_dto.name
        ):
            raise BookException.BookAlreadyExists(input_dto.name)

        book = self.get_book_by_id(id)

        for key, value in input_dto.__dict__.items():
            if value is not None:
                self._update_fields(book, key, value)

        db.session.commit()

        return book

    def _are_there_name_in_request(self, name: str | None) -> bool:
        return name is not None

    def _update_fields(self, book: Book, key: str, value: Any):
        if key not in ('id_book_kind', 'id_book_genre'):
            getattr(book, f'update_{key.strip()}')(value)
        else:
            if key == 'id_book_kind':
                book_kind = self._get_book_kind_by_id(value)
                book.book_kind = book_kind
            else:
                book_genre = self._get_book_genre_by_id(value)
                book.book_genre = book_genre
