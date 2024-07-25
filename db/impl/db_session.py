from typing import Sequence, TypeVar

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.pagination import Pagination
from injector import inject
from sqlalchemy import Select

from exception import GeneralException
from model.base import Model

from .. import IDbSession

TModel = TypeVar('TModel')


@inject
class DbSession(IDbSession):
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def paginate(self, query: Select[tuple[TModel]], *, page: int) -> Pagination:
        with self.db.session.no_autoflush:
            try:
                return self.db.paginate(
                    query,
                    page=page,
                    per_page=20,
                )
            except Exception as e:
                raise GeneralException.PaginationPageDoesntExist(page)

    def get_by_id(self, model: type[TModel], id: str) -> TModel | None:
        with self.db.session.no_autoflush:
            return self.db.session.get(model, id)

    def get_one(self, query: Select[tuple[TModel]]) -> TModel | None:
        with self.db.session.no_autoflush:
            return self.db.session.execute(query).scalar()

    def get_many(self, query: Select[tuple[TModel]]) -> Sequence[TModel]:
        with self.db.session.no_autoflush:
            return self.db.session.execute(query).scalars().all()

    def update(self) -> None:
        self.db.session.commit()

    def add(self, model: Model) -> None:
        self.db.session.add(model)
        self.db.session.commit()

    def delete(self, model: Model) -> None:
        self.db.session.delete(model)
        self.db.session.commit()
