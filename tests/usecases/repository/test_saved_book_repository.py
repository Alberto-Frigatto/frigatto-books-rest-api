from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from db import IDbSession
from exception import SavedBookException
from model import Book, SavedBook, User
from repository.impl import SavedBookRepository


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_db_session() -> Mock:
    return create_autospec(IDbSession)


@pytest.fixture
def saved_book_repository(mock_db_session: Mock) -> SavedBookRepository:
    return SavedBookRepository(mock_db_session)


@pytest.fixture
def user(app: Flask) -> User:
    with app.app_context():
        mock_user = User(
            'frigatto',
            'Senha@123',
            'http://localhost/users/photos/test.jpg',
        )
        mock_user.id = 1

        return mock_user


def test_get_all_saved_books(
    saved_book_repository: SavedBookRepository, app: Flask, mock_db_session: Mock, user: User
):
    with app.app_context(), patch('flask_jwt_extended.utils.get_current_user', return_value=user):
        mock_saved_book = Mock(SavedBook)
        mock_saved_book.book = Mock(Book)

        mock_pagination = Mock(Pagination)
        mock_pagination.items = [mock_saved_book for _ in range(10)]
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
        result = saved_book_repository.get_all(page)

        assert isinstance(result, Pagination)
        assert all(isinstance(item, Book) for item in result.items)
        assert result.total == mock_pagination.total
        assert result.page == mock_pagination.page
        assert result.pages == mock_pagination.pages
        assert result.per_page == mock_pagination.per_page
        assert result.has_prev == mock_pagination.has_prev
        assert result.has_next == mock_pagination.has_next
        assert result.prev_num == mock_pagination.prev_num
        assert result.next_num == mock_pagination.next_num

        mock_db_session.paginate.assert_called_once()


def test_add_saved_book(
    saved_book_repository: SavedBookRepository, app: Flask, mock_db_session: Mock, user: User
):
    with app.app_context(), patch('flask_jwt_extended.utils.get_current_user', return_value=user):
        mock_saved_book = Mock(SavedBook)
        result = saved_book_repository.add(mock_saved_book)

        assert result is None

        mock_db_session.add.assert_called_once_with(mock_saved_book)


def test_when_try_to_save_a_book_already_saved_raises_BookAlreadySaved(
    saved_book_repository: SavedBookRepository, app: Flask, user: User
):
    with pytest.raises(SavedBookException.BookAlreadySaved), app.app_context():
        with patch('flask_jwt_extended.utils.get_current_user', return_value=user), patch(
            'repository.impl.saved_book_repository.SavedBookRepository._saved_book_already_exists',
            return_value=True,
        ):
            mock_saved_book = Mock(SavedBook)
            saved_book_repository.add(mock_saved_book)


def test_delete_saved_book(
    saved_book_repository: SavedBookRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_saved_book = Mock(SavedBook)

        result = saved_book_repository.delete(mock_saved_book)

        assert result is None

        mock_db_session.delete.assert_called_once_with(mock_saved_book)


def test_get_saved_book_by_id_book(
    saved_book_repository: SavedBookRepository, app: Flask, mock_db_session: Mock, user: User
):
    with app.app_context(), patch('flask_jwt_extended.utils.get_current_user', return_value=user):
        mock_saved_book = Mock(SavedBook)
        mock_db_session.get_one = Mock(return_value=mock_saved_book)

        book_id = '1'
        result = saved_book_repository.get_by_id_book(book_id)

        assert isinstance(result, SavedBook)
        assert result == mock_saved_book

        mock_db_session.get_one.assert_called_once()


def test_when_try_to_get_saved_book_by_id_book_from_book_does_not_has_saved_raises_BookIsNotSaved(
    saved_book_repository: SavedBookRepository, app: Flask, mock_db_session: Mock, user: User
):
    with pytest.raises(SavedBookException.BookIsNotSaved), app.app_context():
        with patch('flask_jwt_extended.utils.get_current_user', return_value=user):
            mock_db_session.get_one = Mock(return_value=None)

            book_id = '1'
            saved_book_repository.get_by_id_book(book_id)
