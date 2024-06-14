from typing import Sequence

from sqlalchemy import Select, select

from db import db
from model import Book
from repository import BookGenreRepository, BookKindRepository

select_book = Select[tuple[Book]]


class SearchRepository:
    book_kind_repository = BookKindRepository()
    book_genre_repository = BookGenreRepository()

    def search(self, query: str | None, filter: dict) -> Sequence[Book]:
        sql_query = self._build_query(query, filter)

        return db.session.execute(sql_query).scalars().all()

    def _build_query(self, search_query: str | None, search_filter: dict | None) -> select_book:
        sql_query = select(Book).order_by(Book.id)

        if search_query is not None:
            sql_query = self._apply_search_query(sql_query, search_query)

        if search_filter is not None:
            sql_query = self._apply_filters(sql_query, search_filter)

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

    def _apply_filters(
        self,
        sql_query: select_book,
        search_filter: dict,
    ) -> select_book:
        filters = (
            self._apply_kind_filter,
            self._apply_genre_filter,
            self._apply_release_year_filter,
            self._apply_price_filter,
        )

        for filter in filters:
            sql_query = filter(sql_query, search_filter)

        return sql_query

    def _apply_kind_filter(self, sql_query: select_book, search_filter: dict) -> select_book:
        id_kind: int | None = search_filter.get('id_kind', None)

        if id_kind and self._book_kind_exists(id_kind):
            sql_query = sql_query.filter_by(id_kind=id_kind)

        return sql_query

    def _apply_genre_filter(self, sql_query: select_book, search_filter: dict) -> select_book:
        id_genre: int | None = search_filter.get('id_genre', None)

        if id_genre and self._book_genre_exists(id_genre):
            sql_query = sql_query.filter_by(id_genre=id_genre)

        return sql_query

    def _apply_release_year_filter(
        self, sql_query: select_book, search_filter: dict
    ) -> select_book:
        release_year: int | None = search_filter.get('release_year', None)

        if release_year:
            sql_query = sql_query.filter_by(release_year=release_year)

        return sql_query

    def _apply_price_filter(self, sql_query: select_book, search_filter: dict) -> select_book:
        price: dict | None = search_filter.get('price', None)

        if price is not None:
            min_price: int | float | None = price.get('min', None)
            max_price: int | float | None = price.get('max', None)

            if min_price is not None:
                sql_query = sql_query.where(Book.price >= min_price)

            if max_price is not None:
                sql_query = sql_query.where(Book.price <= max_price)

        return sql_query

    def _book_kind_exists(self, id: int | None) -> bool:
        return bool(self.book_kind_repository.get_by_id(str(id) if id is not None else ''))

    def _book_genre_exists(self, id: int | None) -> bool:
        return bool(self.book_genre_repository.get_by_id(str(id) if id is not None else ''))
