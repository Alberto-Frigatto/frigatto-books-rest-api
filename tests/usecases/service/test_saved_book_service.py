from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from model import Book, SavedBook, User
from repository import IBookRepository, ISavedBookRepository
from service.impl import SavedBookService


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_book_repository() -> Mock:
    return create_autospec(IBookRepository)


@pytest.fixture
def mock_saved_book_repository() -> Mock:
    return create_autospec(ISavedBookRepository)


@pytest.fixture
def saved_book_service(
    mock_book_repository: Mock, mock_saved_book_repository: Mock
) -> SavedBookService:
    return SavedBookService(mock_book_repository, mock_saved_book_repository)


@pytest.fixture
def user(app: Flask) -> User:
    with app.app_context():
        return User(
            'frigatto',
            'Senha@123',
            'http://localhost/users/photos/test.jpg',
        )


def test_get_all_saved_books(
    saved_book_service: SavedBookService,
    app: Flask,
    mock_saved_book_repository: Mock,
):
    with app.app_context():
        mock_pagination = Mock(Pagination)
        mock_pagination.items = [Mock(Book) for _ in range(3)]
        mock_pagination.total = len(mock_pagination.items)
        mock_pagination.page = 1
        mock_pagination.pages = 1
        mock_pagination.per_page = 20
        mock_pagination.has_prev = False
        mock_pagination.has_next = False
        mock_pagination.prev_num = None
        mock_pagination.next_num = None

        mock_saved_book_repository.get_all = Mock(return_value=mock_pagination)

        page = 1
        result = saved_book_service.get_all_saved_books(page)

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

        mock_saved_book_repository.get_all.assert_called_once_with(page)


def test_save_book(
    saved_book_service: SavedBookService,
    app: Flask,
    mock_saved_book_repository: Mock,
    mock_book_repository: Mock,
    user: User,
):
    with app.app_context(), patch('flask_jwt_extended.utils.get_current_user', return_value=user):
        mock_book = Mock(Book)
        mock_book_repository.get_by_id = Mock(return_value=mock_book)

        book_id = '1'
        result = saved_book_service.save_book(book_id)

        assert isinstance(result, Book)
        assert result == mock_book

        mock_book_repository.get_by_id.assert_called_once_with(book_id)
        mock_saved_book_repository.add.assert_called_once()


def test_delete_saved_book(
    saved_book_service: SavedBookService,
    app: Flask,
    mock_saved_book_repository: Mock,
    mock_book_repository: Mock,
    user: User,
):
    with app.app_context(), patch('flask_jwt_extended.utils.get_current_user', return_value=user):
        mock_book = Mock(Book)
        mock_book_repository.get_by_id = Mock(return_value=mock_book)

        mock_saved_book = Mock(SavedBook)
        mock_saved_book_repository.get_by_id_book = Mock(return_value=mock_saved_book)

        book_id = '1'
        result = saved_book_service.delete_saved_book(book_id)

        assert result is None

        mock_book_repository.get_by_id.assert_called_once_with(book_id)
        mock_saved_book_repository.get_by_id_book.assert_called_once_with(str(mock_book.id))
        mock_saved_book_repository.delete.assert_called_once_with(mock_saved_book)
