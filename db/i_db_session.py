from abc import ABC, abstractmethod
from typing import Sequence, TypeVar

from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import Select

from model.base import Model

TModel = TypeVar('TModel')


class IDbSession(ABC):
    @abstractmethod
    def paginate(self, query: Select[tuple[TModel]], *, page: int) -> Pagination:
        pass

    @abstractmethod
    def get_by_id(self, model: type[TModel], id: str) -> TModel | None:
        pass

    @abstractmethod
    def get_one(self, query: Select[tuple[TModel]]) -> TModel | None:
        pass

    @abstractmethod
    def get_many(self, query: Select[tuple[TModel]]) -> Sequence[TModel]:
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
