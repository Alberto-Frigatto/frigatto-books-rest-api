from typing import Any, Sequence

from flask import request
from sqlalchemy import select

from db import db
from handle_errors import CustomError
from models import BookKind


class BookKindsController:
    def get_all_book_kinds(self) -> Sequence[BookKind]:
        query = select(BookKind).order_by(BookKind.id)
        book_kinds = db.session.execute(query).scalars().all()

        return book_kinds

    def get_book_kind_by_id(self, id: int) -> BookKind:
        query = select(BookKind).filter_by(id=id)
        book_kind = db.session.execute(query).scalar()

        if book_kind is None:
            raise CustomError('BookKindDoesntExists')

        return book_kind

    def create_book_kind(self) -> BookKind:
        if not self._are_there_data():
            raise CustomError('NoDataSent')

        data = request.json

        if not self._is_data_valid(data):
            raise CustomError('InvalidDataSent')

        new_book_kind = BookKind(data['kind'])

        if self._book_kind_already_exists(new_book_kind):
            raise CustomError('BookKindAlreadyExists')

        db.session.add(new_book_kind)
        db.session.commit()

        return new_book_kind

    def _are_there_data(self) -> bool:
        return request.content_length

    def _is_data_valid(self, data: Any) -> bool:
        return isinstance(data, dict) and 'kind' in data.keys()

    def _book_kind_already_exists(self, book_kind: BookKind | str) -> bool:
        query = select(BookKind).filter_by(
            kind=(
                book_kind.kind
                if isinstance(book_kind, BookKind)
                else (book_kind.strip().lower() if isinstance(book_kind, str) else book_kind)
            )
        )
        return bool(db.session.execute(query).scalar())

    def delete_book_kind(self, id: int) -> None:
        book_kind = self.get_book_kind_by_id(id)

        db.session.delete(book_kind)
        db.session.commit()

    def update_book_kind(self, id: int) -> BookKind:
        book_kind = self.get_book_kind_by_id(id)

        if not self._are_there_data():
            raise CustomError('NoDataSent')

        data = request.json

        if not self._is_data_valid(data):
            raise CustomError('InvalidDataSent')

        if self._book_kind_already_exists(data['kind']):
            raise CustomError('BookKindAlreadyExists')

        book_kind.update_kind(data['kind'])
        db.session.commit()

        return book_kind
