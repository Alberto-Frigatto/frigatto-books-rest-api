from abc import ABC, abstractmethod
from typing import Any, Sequence, TypeVar

from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import Select

from .database import db

TModel = TypeVar("TModel", db.Model, Any)
Model = db.Model


class IDbSession(ABC):
    @abstractmethod
    def paginate(self, query: Select[tuple[type[TModel]]], *, page: int) -> Pagination:
        pass

    @abstractmethod
    def get_by_id(self, model: type[TModel], id: str) -> type[TModel] | None:
        pass

    @abstractmethod
    def get_one(self, query: Select[tuple[type[TModel]]]) -> type[TModel] | None:
        pass

    @abstractmethod
    def get_many(self, query: Select[tuple[type[TModel]]]) -> Sequence[type[TModel]]:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def add(self, model: Model) -> None:
        pass

    @abstractmethod
    def delete(self, model: Model) -> None:
        pass
