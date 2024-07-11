from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask

from app import create_app
from db import IDbSession
from exception import BookKeywordException
from model import BookKeyword
from repository.impl import BookKeywordRepository


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_db_session() -> Mock:
    return create_autospec(IDbSession)


@pytest.fixture
def book_keyword_repository(mock_db_session: Mock) -> BookKeywordRepository:
    return BookKeywordRepository(mock_db_session)


def test_get_book_keyword_by_id(
    book_keyword_repository: BookKeywordRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_book_keyword = Mock(BookKeyword)
        mock_db_session.get_by_id = Mock(return_value=mock_book_keyword)

        book_keyword_id = '1'
        result = book_keyword_repository.get_by_id(book_keyword_id)

        assert isinstance(result, BookKeyword)
        assert result == mock_book_keyword

        mock_db_session.get_by_id.assert_called_once_with(BookKeyword, book_keyword_id)


def test_when_try_to_get_book_keyword_does_not_exists_raises_BookKeywordDoesntExists(
    book_keyword_repository: BookKeywordRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context(), pytest.raises(BookKeywordException.BookKeywordDoesntExists):
        mock_db_session.get_by_id = Mock(return_value=None)

        book_keyword_id = '1'
        book_keyword_repository.get_by_id(book_keyword_id)


def test_add_book_keyword(
    book_keyword_repository: BookKeywordRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_book_keyword = Mock(BookKeyword)

        result = book_keyword_repository.add(mock_book_keyword)

        assert result is None

        mock_db_session.add.assert_called_once_with(mock_book_keyword)


def test_delete_book_keyword(
    book_keyword_repository: BookKeywordRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_book_keyword = Mock(BookKeyword)

        result = book_keyword_repository.delete(mock_book_keyword)

        assert result is None

        mock_db_session.delete.assert_called_once_with(mock_book_keyword)
