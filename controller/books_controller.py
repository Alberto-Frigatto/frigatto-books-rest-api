import os
from typing import Sequence

from flask import request
from sqlalchemy import select
from werkzeug.datastructures import ImmutableMultiDict

from db import db
from handle_errors import CustomError
from image_uploader import BooksImageUploader
from model import Book, BookGenre, BookImg, BookKeyword, BookKind

from .controller import Controller

file_path = str
mimetype = str


class BooksController(Controller):
    def get_all_books(self) -> Sequence[Book]:
        query = select(Book).order_by(Book.id)
        books = db.session.execute(query).scalars().all()

        return books

    def get_book_by_id(self, id: str) -> Book:
        book = db.session.get(Book, id)

        if book is None:
            raise CustomError('BookDoesntExists')

        return book

    def create_book(self) -> Book:
        if not super().are_there_data():
            raise CustomError('NoDataSent')

        form_data = request.form.to_dict()
        files_data = request.files

        if not self._is_data_valid_for_create(form_data, files_data):
            raise CustomError('InvalidDataSent')

        if self._book_already_exists(form_data['name']):
            raise CustomError('BookAlreadyExists')

        new_book = Book(
            form_data['name'],
            form_data['price'],
            form_data['author'],
            form_data['release_year'],
        )

        book_kind = self._get_book_kind_by_id(form_data['id_book_kind'])
        book_genre = self._get_book_genre_by_id(form_data['id_book_genre'])
        book_keywords = self._extract_book_keywords(form_data['keywords'])
        book_imgs = [BooksImageUploader(image) for image in files_data.getlist('imgs')]

        new_book.book_kind = book_kind
        new_book.book_genre = book_genre
        new_book.book_keywords = book_keywords
        new_book.book_imgs = [BookImg(img.get_url()) for img in book_imgs]

        for img in book_imgs:
            img.save()

        db.session.add(new_book)
        db.session.commit()

        return new_book

    def _is_data_valid_for_create(self, form_data: dict, files_data: ImmutableMultiDict) -> bool:
        max_photo_qty = 5

        imgs_qty = len(files_data.getlist('imgs'))

        return (
            all(
                key in form_data.keys()
                for key in (
                    'name',
                    'price',
                    'author',
                    'release_year',
                    'keywords',
                    'id_book_kind',
                    'id_book_genre',
                )
            )
            and imgs_qty
            and imgs_qty <= max_photo_qty
        )

    def _book_already_exists(self, name: str) -> bool:
        query = select(Book).where(
            Book.name.ilike(name.strip().lower() if isinstance(name, str) else name)
        )

        return bool(db.session.execute(query).scalar())

    def _get_book_kind_by_id(self, id: str) -> BookKind:
        book_kind = db.session.get(BookKind, id)

        if book_kind is None:
            raise CustomError('BookKindDoesntExists')

        return book_kind

    def _get_book_genre_by_id(self, id: str) -> BookGenre:
        book_genre = db.session.get(BookGenre, id)

        if book_genre is None:
            raise CustomError('BookGenreDoesntExists')

        return book_genre

    def _extract_book_keywords(self, keywords: str) -> list[BookKeyword]:
        if not self._is_book_keywords_valid(keywords):
            raise CustomError('InvalidDataSent')

        separator = ';'

        return [BookKeyword(keyword) for keyword in keywords.strip().split(separator) if keyword]

    def _is_book_keywords_valid(self, keywords: str) -> bool:
        return isinstance(keywords, str) and keywords

    def delete_book(self, id: str) -> None:
        book = self.get_book_by_id(id)

        for book_img in book.book_imgs:
            BooksImageUploader.delete(book_img.img_url)

        db.session.delete(book)
        db.session.commit()

    def update_book(self, id: str) -> Book:
        if not super().are_there_data():
            raise CustomError('NoDataSent')

        form_data = request.form.to_dict()

        if not self._is_data_valid_for_update(form_data):
            raise CustomError('InvalidDataSent')

        if self._are_there_name_in_request(form_data) and self._book_already_exists(
            form_data['name']
        ):
            raise CustomError('BookAlreadyExists')

        book = self.get_book_by_id(id)

        for key, value in list(form_data.items()):
            self._update_fields(book, key, value)

        db.session.commit()

        return book

    def _is_data_valid_for_update(self, form_data: dict) -> bool:
        allowed_keys = ('name', 'price', 'author', 'release_year', 'id_book_kind', 'id_book_genre')

        return all(key in allowed_keys for key in form_data.keys())

    def _are_there_name_in_request(self, form_data: dict) -> bool:
        return 'name' in form_data.keys()

    def _update_fields(self, book: Book, key: str, value: str):
        if key not in ('id_book_kind', 'id_book_genre'):
            getattr(book, f'update_{key.strip()}')(value)
        else:
            if key == 'id_book_kind':
                book_kind = self._get_book_kind_by_id(value)
                book.book_kind = book_kind
            else:
                book_genre = self._get_book_genre_by_id(value)
                book.book_genre = book_genre
