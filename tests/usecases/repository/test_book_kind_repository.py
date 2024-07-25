from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from db import IDbSession
from exception import BookKindException
from model import Book, BookKind
from repository.impl import BookKindRepository


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_db_session() -> Mock:
    return create_autospec(IDbSession)


@pytest.fixture
def book_kind_repository(mock_db_session: Mock) -> BookKindRepository:
    return BookKindRepository(mock_db_session)


def test_get_all_book_kinds(
    book_kind_repository: BookKindRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_pagination = Mock(Pagination)
        mock_pagination.items = [Mock(BookKind) for _ in range(10)]
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
        result = book_kind_repository.get_all(page)

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


def test_get_book_kind_by_id(
    book_kind_repository: BookKindRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_book_kind = Mock(BookKind)
        mock_db_session.get_by_id = Mock(return_value=mock_book_kind)

        book_kind_id = '1'
        result = book_kind_repository.get_by_id(book_kind_id)

        assert isinstance(result, BookKind)
        assert result == mock_book_kind

        mock_db_session.get_by_id.assert_called_once_with(BookKind, book_kind_id)


def test_when_try_to_get_book_kind_by_id_from_book_kind_does_not_exists_raises_BookKindDoesntExists(
    book_kind_repository: BookKindRepository, app: Flask, mock_db_session: Mock
):
    with pytest.raises(BookKindException.BookKindDoesntExist), app.app_context():
        mock_db_session.get_by_id = Mock(return_value=None)

        book_kind_id = '1'
        book_kind_repository.get_by_id(book_kind_id)


def test_create_book_kind(
    book_kind_repository: BookKindRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_db_session.get_one = Mock(return_value=None)

        mock_book_kind = Mock(BookKind)
        result = book_kind_repository.add(mock_book_kind)

        assert result is None

        mock_db_session.get_one.assert_called_once()
        mock_db_session.add.assert_called_once_with(mock_book_kind)


def test_when_try_to_create_book_kind_already_exists_raises_BookKindAlreadyExists(
    book_kind_repository: BookKindRepository, app: Flask, mock_db_session: Mock
):
    with pytest.raises(BookKindException.BookKindAlreadyExists), app.app_context():
        mock_db_session.get_one = Mock(return_value=Mock(BookKind))

        book_kind_repository.add(Mock(BookKind))


def test_delete_book_kind(
    book_kind_repository: BookKindRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_book_kind = Mock(BookKind)
        mock_db_session.get_by_id = Mock(return_value=mock_book_kind)
        mock_db_session.get_many = Mock(return_value=None)

        book_kind_id = '1'
        result = book_kind_repository.delete(book_kind_id)

        assert result is None

        mock_db_session.get_many.assert_called_once()
        mock_db_session.get_by_id.assert_called_once_with(BookKind, book_kind_id)
        mock_db_session.delete.assert_called_once()


def test_when_try_to_delete_book_kind_with_linked_books_raises_ThereAreLinkedBooksWithThisBookKind(
    book_kind_repository: BookKindRepository, app: Flask, mock_db_session: Mock
):
    with pytest.raises(BookKindException.ThereAreLinkedBooksWithThisBookKind), app.app_context():
        mock_db_session.get_by_id = Mock(return_value=Mock(BookKind))
        mock_db_session.get_many = Mock(return_value=[Mock(Book) for _ in range(2)])

        book_kind_id = '1'
        book_kind_repository.delete(book_kind_id)


def test_update_book_kind(
    book_kind_repository: BookKindRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_db_session.get_one = Mock(return_value=None)

        mock_book_kind = Mock(BookKind)
        result = book_kind_repository.update(mock_book_kind)

        assert result is None

        mock_db_session.get_one.assert_called_once()
        mock_db_session.update.assert_called_once()


def test_when_try_to_update_book_kind_with_kind_already_exists_raises_BookKindAlreadyExists(
    book_kind_repository: BookKindRepository, app: Flask, mock_db_session: Mock
):
    with pytest.raises(BookKindException.BookKindAlreadyExists), app.app_context():
        mock_db_session.get_one = Mock(return_value=Mock(BookKind))

        book_kind_repository.update(Mock(BookKind))
