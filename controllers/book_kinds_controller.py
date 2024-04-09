from typing import Sequence

from flask import request
from sqlalchemy import select

from db import db
from handle_errors import CustomError
from models import BookKind


class BookKindsController:
    def get_all_book_kinds(self) -> Sequence[BookKind]:
        book_kinds = db.session.execute(select(BookKind).order_by(BookKind.id)).scalars().all()

        return book_kinds

    def get_book_kind_by_id(self, id: int) -> BookKind:
        book_kind = db.session.execute(select(BookKind).filter_by(id=id)).scalar()

        if book_kind is None:
            raise CustomError('BookKindDoesntExists')

        return book_kind

    def create_book_kind(self):
        if not self._are_there_data():
            raise CustomError('NoDataSent')

        book_kind = request.json['kind'].lower()

        if self._book_kind_already_exists(book_kind):
            raise CustomError('BookKindAlreadyExists')

        new_book_kind = BookKind(book_kind)

        db.session.add(new_book_kind)
        db.session.commit()

        return new_book_kind

    def _are_there_data(self) -> bool:
        return request.content_length

    def _book_kind_already_exists(self, book_kind) -> bool:
        return bool(db.session.execute(select(BookKind).filter_by(kind=book_kind)).scalar())
