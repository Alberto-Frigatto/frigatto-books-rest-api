from typing import Sequence

from sqlalchemy import Select, select

from db import db
from dto.input import SearchDTO
from exception import BookGenreException, BookKindException
from model import Book, BookGenre, BookKind


class SearchController:
    def search_books(self, input_dto: SearchDTO) -> Sequence[Book]:
        sql_query = self._build_base_query(input_dto.query, input_dto.filter)
        matched_books = self._get_books_from_query(sql_query)

        return matched_books

    def _build_base_query(
        self, search_query: str | None, search_filter: dict | None
    ) -> Select[tuple[Book]]:
        sql_query = select(Book).order_by(Book.id)

        if search_query is not None:
            sql_query = self._apply_search_query(sql_query, search_query)

        if search_filter is not None:
            sql_query = self._apply_filters(sql_query, search_filter)

        return sql_query

    def _apply_search_query(
        self,
        sql_query: Select[tuple[Book]],
        search_query: str,
    ) -> Select[tuple[Book]]:
        search_query = search_query.strip()
        return sql_query.where(
            Book.name.icontains(search_query)
            | Book.author.icontains(search_query)
            | Book.book_keywords.any(keyword=search_query.lower())
        )

    def _apply_filters(
        self,
        sql_query: Select[tuple[Book]],
        search_filter: dict,
    ) -> Select[tuple[Book]]:
        filters = (
            self._apply_kind_filter,
            self._apply_genre_filter,
            self._apply_release_year_filter,
            self._apply_price_filter,
        )

        for filter in filters:
            sql_query = filter(sql_query, search_filter)

        return sql_query

    def _apply_kind_filter(
        self, sql_query: Select[tuple[Book]], search_filter: dict
    ) -> Select[tuple[Book]]:
        id_kind: int | None = search_filter.get('id_kind', None)

        if id_kind and self._book_kind_exists(id_kind):
            sql_query = sql_query.filter_by(id_kind=id_kind)

        return sql_query

    def _apply_genre_filter(
        self, sql_query: Select[tuple[Book]], search_filter: dict
    ) -> Select[tuple[Book]]:
        id_genre: int | None = search_filter.get('id_genre', None)

        if id_genre and self._book_genre_exists(id_genre):
            sql_query = sql_query.filter_by(id_genre=id_genre)

        return sql_query

    def _apply_release_year_filter(
        self, sql_query: Select[tuple[Book]], search_filter: dict
    ) -> Select[tuple[Book]]:
        release_year: int | None = search_filter.get('release_year', None)

        if release_year:
            sql_query = sql_query.filter_by(release_year=release_year)

        return sql_query

    def _apply_price_filter(
        self, sql_query: Select[tuple[Book]], search_filter: dict
    ) -> Select[tuple[Book]]:
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
        book_kind = db.session.get(BookKind, id)

        if book_kind is None:
            raise BookKindException.BookKindDoesntExists(str(id))

        return bool(book_kind)

    def _book_genre_exists(self, id: int | None) -> bool:
        book_genre = db.session.get(BookGenre, id)

        if book_genre is None:
            raise BookGenreException.BookGenreDoesntExists(str(id))

        return bool(book_genre)

    def _get_books_from_query(self, sql_query: Select[tuple[Book]]) -> Sequence[Book]:
        return db.session.execute(sql_query).scalars().all()
