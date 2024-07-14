from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from controller.impl import SavedBookController
from model import Book
from service import ISavedBookService


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_service() -> Mock:
    return create_autospec(ISavedBookService)


@pytest.fixture
def saved_book_controller(mock_service: Mock) -> SavedBookController:
    return SavedBookController(mock_service)


def test_get_all_saved_books(
    saved_book_controller: SavedBookController, app: Flask, mock_service: Mock
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

        mock_service.get_all_saved_books = Mock(return_value=mock_pagination)

        page = 1

        result = saved_book_controller.get_all_saved_books(page)

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

        mock_service.get_all_saved_books.assert_called_once_with(page)


def test_save_book(saved_book_controller: SavedBookController, app: Flask, mock_service: Mock):
    with app.app_context():
        mock_book = Mock(Book)
        mock_service.save_book = Mock(return_value=mock_book)

        book_id = '1'
        result = saved_book_controller.save_book(book_id)

        assert isinstance(result, Book)
        assert result == mock_book

        mock_service.save_book.assert_called_once_with(book_id)


def test_saved_delete_book(
    saved_book_controller: SavedBookController, app: Flask, mock_service: Mock
):
    with app.app_context():
        book_id = '1'
        result = saved_book_controller.delete_saved_book(book_id)

        assert result is None

        mock_service.delete_saved_book.assert_called_once_with(book_id)
