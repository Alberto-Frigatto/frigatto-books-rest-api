from decimal import Decimal
from typing import Sequence

from injector import inject
from sqlalchemy import Select, select
from sqlalchemy.orm import scoped_session

from model import Book
from repository import BookGenreRepository, BookKindRepository

select_book = Select[tuple[Book]]


@inject
class SearchRepository:
    def __init__(
        self,
        book_kind_repository: BookKindRepository,
        book_genre_repository: BookGenreRepository,
        session: scoped_session,
    ) -> None:
        self.book_kind_repository = book_kind_repository
        self.book_genre_repository = book_genre_repository
        self.session = session

    def search(
        self,
        *,
        query: str | None,
        id_book_kind: int | None,
        id_book_genre: int | None,
        release_year: int | None,
        min_price: Decimal | None,
        max_price: Decimal | None,
    ) -> Sequence[Book]:
        sql_query = self._build_query(
            query, id_book_kind, id_book_genre, release_year, min_price, max_price
        )

        return self.session.execute(sql_query).scalars().all()

    def _build_query(
        self,
        search_query: str | None,
        id_book_kind: int | None,
        id_book_genre: int | None,
        release_year: int | None,
        min_price: Decimal | None,
        max_price: Decimal | None,
    ) -> select_book:
        sql_query = select(Book).order_by(Book.id)

        if search_query is not None:
            sql_query = self._apply_search_query(sql_query, search_query)

        if id_book_kind is not None:
            sql_query = self._apply_kind(sql_query, id_book_kind)

        if id_book_genre is not None:
            sql_query = self._apply_genre(sql_query, id_book_genre)

        if release_year is not None:
            sql_query = self._apply_release_year(sql_query, release_year)

        if min_price is not None:
            sql_query = self._apply_min_price(sql_query, min_price)

        if max_price is not None:
            sql_query = self._apply_max_price(sql_query, max_price)

        return sql_query

    def _apply_search_query(
        self,
        sql_query: select_book,
        search_query: str,
    ) -> select_book:
        search_query = search_query.strip()
        return sql_query.where(
            Book.name.icontains(search_query)
            | Book.author.icontains(search_query)
            | Book.book_keywords.any(keyword=search_query.lower())
        )

    def _apply_kind(self, sql_query: select_book, id_kind: int) -> select_book:
        if self._book_kind_exists(id_kind):
            sql_query = sql_query.filter_by(id_kind=id_kind)

        return sql_query

    def _book_kind_exists(self, id: int | None) -> bool:
        return bool(self.book_kind_repository.get_by_id(str(id) if id is not None else ''))

    def _apply_genre(self, sql_query: select_book, id_genre: int) -> select_book:
        if self._book_genre_exists(id_genre):
            sql_query = sql_query.filter_by(id_genre=id_genre)

        return sql_query

    def _book_genre_exists(self, id: int | None) -> bool:
        return bool(self.book_genre_repository.get_by_id(str(id) if id is not None else ''))

    def _apply_release_year(self, sql_query: select_book, release_year: int) -> select_book:
        sql_query = sql_query.filter_by(release_year=release_year)

        return sql_query

    def _apply_min_price(self, sql_query: select_book, min_price: Decimal) -> select_book:
        sql_query = sql_query.where(Book.price >= min_price)

        return sql_query

    def _apply_max_price(self, sql_query: select_book, max_price: Decimal) -> select_book:
        sql_query = sql_query.where(Book.price <= max_price)

        return sql_query
