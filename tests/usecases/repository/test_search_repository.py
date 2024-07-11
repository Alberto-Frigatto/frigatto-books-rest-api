from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from db import IDbSession
from model import Book
from repository import IBookGenreRepository, IBookKindRepository
from repository.impl import SearchRepository


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_db_session() -> Mock:
    return create_autospec(IDbSession)


@pytest.fixture
def mock_book_kind_repository() -> Mock:
    return create_autospec(IBookKindRepository)


@pytest.fixture
def mock_book_genre_repository() -> Mock:
    return create_autospec(IBookGenreRepository)


@pytest.fixture
def search_repository(
    mock_book_kind_repository: Mock,
    mock_book_genre_repository: Mock,
    mock_db_session: Mock,
) -> SearchRepository:
    return SearchRepository(
        mock_book_kind_repository,
        mock_book_genre_repository,
        mock_db_session,
    )


def test_search_books_by_query(
    search_repository: SearchRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_pagination = Mock(Pagination)
        mock_pagination.items = [Mock(Book) for _ in range(10)]
        mock_pagination.total = len(mock_pagination.items)
        mock_pagination.page = 1
        mock_pagination.pages = 1
        mock_pagination.per_page = 20
        mock_pagination.has_prev = False
        mock_pagination.has_next = False
        mock_pagination.prev_num = None
        mock_pagination.next_num = None

        mock_db_session.paginate = Mock(return_value=mock_pagination)

        page = 1
        result = search_repository.search(
            page=page,
            query=Mock(),
            id_book_genre=None,
            id_book_kind=None,
            max_price=None,
            min_price=None,
            release_year=None,
        )

        assert isinstance(result, Pagination)
        assert result.items == mock_pagination.items
        assert result.total == mock_pagination.total
        assert result.page == mock_pagination.page
        assert result.pages == mock_pagination.pages
        assert result.per_page == mock_pagination.per_page
        assert result.has_prev == mock_pagination.has_prev
        assert result.has_next == mock_pagination.has_next
        assert result.prev_num == mock_pagination.prev_num
        assert result.next_num == mock_pagination.next_num

        mock_db_session.paginate.assert_called_once()


def test_search_books_by_id_book_genre(
    search_repository: SearchRepository,
    app: Flask,
    mock_db_session: Mock,
    mock_book_genre_repository: Mock,
):
    with app.app_context():
        mock_pagination = Mock(Pagination)
        mock_pagination.items = [Mock(Book) for _ in range(10)]
        mock_pagination.total = len(mock_pagination.items)
        mock_pagination.page = 1
        mock_pagination.pages = 1
        mock_pagination.per_page = 20
        mock_pagination.has_prev = False
        mock_pagination.has_next = False
        mock_pagination.prev_num = None
        mock_pagination.next_num = None

        mock_db_session.paginate = Mock(return_value=mock_pagination)

        page = 1
        result = search_repository.search(
            page=page,
            query=None,
            id_book_genre=Mock(),
            id_book_kind=None,
            max_price=None,
            min_price=None,
            release_year=None,
        )

        assert isinstance(result, Pagination)
        assert result.items == mock_pagination.items
        assert result.total == mock_pagination.total
        assert result.page == mock_pagination.page
        assert result.pages == mock_pagination.pages
        assert result.per_page == mock_pagination.per_page
        assert result.has_prev == mock_pagination.has_prev
        assert result.has_next == mock_pagination.has_next
        assert result.prev_num == mock_pagination.prev_num
        assert result.next_num == mock_pagination.next_num

        mock_book_genre_repository.get_by_id.assert_called_once()
        mock_db_session.paginate.assert_called_once()


def test_search_books_by_id_book_kind(
    search_repository: SearchRepository,
    app: Flask,
    mock_db_session: Mock,
    mock_book_kind_repository: Mock,
):
    with app.app_context():
        mock_pagination = Mock(Pagination)
        mock_pagination.items = [Mock(Book) for _ in range(10)]
        mock_pagination.total = len(mock_pagination.items)
        mock_pagination.page = 1
        mock_pagination.pages = 1
        mock_pagination.per_page = 20
        mock_pagination.has_prev = False
        mock_pagination.has_next = False
        mock_pagination.prev_num = None
        mock_pagination.next_num = None

        mock_db_session.paginate = Mock(return_value=mock_pagination)

        page = 1
        result = search_repository.search(
            page=page,
            query=None,
            id_book_genre=None,
            id_book_kind=Mock(),
            max_price=None,
            min_price=None,
            release_year=None,
        )

        assert isinstance(result, Pagination)
        assert result.items == mock_pagination.items
        assert result.total == mock_pagination.total
        assert result.page == mock_pagination.page
        assert result.pages == mock_pagination.pages
        assert result.per_page == mock_pagination.per_page
        assert result.has_prev == mock_pagination.has_prev
        assert result.has_next == mock_pagination.has_next
        assert result.prev_num == mock_pagination.prev_num
        assert result.next_num == mock_pagination.next_num

        mock_book_kind_repository.get_by_id.assert_called_once()
        mock_db_session.paginate.assert_called_once()


def test_search_books_max_price(
    search_repository: SearchRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_pagination = Mock(Pagination)
        mock_pagination.items = [Mock(Book) for _ in range(10)]
        mock_pagination.total = len(mock_pagination.items)
        mock_pagination.page = 1
        mock_pagination.pages = 1
        mock_pagination.per_page = 20
        mock_pagination.has_prev = False
        mock_pagination.has_next = False
        mock_pagination.prev_num = None
        mock_pagination.next_num = None

        mock_db_session.paginate = Mock(return_value=mock_pagination)

        page = 1
        result = search_repository.search(
            page=page,
            query=None,
            id_book_genre=None,
            id_book_kind=None,
            max_price=Mock(),
            min_price=None,
            release_year=None,
        )

        assert isinstance(result, Pagination)
        assert result.items == mock_pagination.items
        assert result.total == mock_pagination.total
        assert result.page == mock_pagination.page
        assert result.pages == mock_pagination.pages
        assert result.per_page == mock_pagination.per_page
        assert result.has_prev == mock_pagination.has_prev
        assert result.has_next == mock_pagination.has_next
        assert result.prev_num == mock_pagination.prev_num
        assert result.next_num == mock_pagination.next_num

        mock_db_session.paginate.assert_called_once()


def test_search_books_min_price(
    search_repository: SearchRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_pagination = Mock(Pagination)
        mock_pagination.items = [Mock(Book) for _ in range(10)]
        mock_pagination.total = len(mock_pagination.items)
        mock_pagination.page = 1
        mock_pagination.pages = 1
        mock_pagination.per_page = 20
        mock_pagination.has_prev = False
        mock_pagination.has_next = False
        mock_pagination.prev_num = None
        mock_pagination.next_num = None

        mock_db_session.paginate = Mock(return_value=mock_pagination)

        page = 1
        result = search_repository.search(
            page=page,
            query=None,
            id_book_genre=None,
            id_book_kind=None,
            max_price=None,
            min_price=Mock(),
            release_year=None,
        )

        assert isinstance(result, Pagination)
        assert result.items == mock_pagination.items
        assert result.total == mock_pagination.total
        assert result.page == mock_pagination.page
        assert result.pages == mock_pagination.pages
        assert result.per_page == mock_pagination.per_page
        assert result.has_prev == mock_pagination.has_prev
        assert result.has_next == mock_pagination.has_next
        assert result.prev_num == mock_pagination.prev_num
        assert result.next_num == mock_pagination.next_num

        mock_db_session.paginate.assert_called_once()


def test_search_books_release_year(
    search_repository: SearchRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_pagination = Mock(Pagination)
        mock_pagination.items = [Mock(Book) for _ in range(10)]
        mock_pagination.total = len(mock_pagination.items)
        mock_pagination.page = 1
        mock_pagination.pages = 1
        mock_pagination.per_page = 20
        mock_pagination.has_prev = False
        mock_pagination.has_next = False
        mock_pagination.prev_num = None
        mock_pagination.next_num = None

        mock_db_session.paginate = Mock(return_value=mock_pagination)

        page = 1
        result = search_repository.search(
            page=page,
            query=None,
            id_book_genre=None,
            id_book_kind=None,
            max_price=None,
            min_price=None,
            release_year=Mock(),
        )

        assert isinstance(result, Pagination)
        assert result.items == mock_pagination.items
        assert result.total == mock_pagination.total
        assert result.page == mock_pagination.page
        assert result.pages == mock_pagination.pages
        assert result.per_page == mock_pagination.per_page
        assert result.has_prev == mock_pagination.has_prev
        assert result.has_next == mock_pagination.has_next
        assert result.prev_num == mock_pagination.prev_num
        assert result.next_num == mock_pagination.next_num

        mock_db_session.paginate.assert_called_once()
