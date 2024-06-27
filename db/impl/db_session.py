from typing import Any, Sequence, TypeVar

from injector import inject
from sqlalchemy import Select
from sqlalchemy.orm import scoped_session

from .. import IDbSession, db

TModel = TypeVar("TModel", db.Model, Any)
Model = db.Model


@inject
class DbSession(IDbSession):
    def __init__(self, session: scoped_session) -> None:
        self.session = session

    def get_by_id(self, model: type[TModel], id: str) -> type[TModel] | None:
        with self.session.no_autoflush:
            return self.session.get(model, id)

    def get_one(self, query: Select[tuple[type[TModel]]]) -> type[TModel] | None:
        with self.session.no_autoflush:
            return self.session.execute(query).scalar()

    def get_many(self, query: Select[tuple[type[TModel]]]) -> Sequence[type[TModel]]:
        with self.session.no_autoflush:
            return self.session.execute(query).scalars().all()

    def update(self) -> None:
        self.session.commit()

    def add(self, model: Model) -> None:
        self.session.add(model)
        self.session.commit()

    def delete(self, model: Model) -> None:
        self.session.delete(model)
        self.session.commit()
