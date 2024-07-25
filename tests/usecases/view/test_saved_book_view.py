from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask, Response
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from controller import ISavedBookController
from model import SavedBook
from view.saved_book_view import SavedBookView


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_controller() -> Mock:
    return create_autospec(ISavedBookController)


def test_save_book(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch(
            'view.saved_book_view.BookOutputDTO.dump', return_value=mock_serialization
        ) as mock_BookOutputDTO_dump, patch(
            'view.saved_book_view.CreatedResponse', return_value=mock_json
        ) as mock_CreatedResponse:
            mock_saved_book = Mock(SavedBook)
            mock_controller.save_book = Mock(return_value=mock_saved_book)

            book_id = Mock()
            result = SavedBookView.save_book(book_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.save_book.assert_called_once_with(book_id)
            mock_BookOutputDTO_dump.assert_called_once_with(mock_saved_book)
            mock_CreatedResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()


def test_get_all_saved_books(app: Flask, mock_controller: Mock):
    mock_page = Mock()
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch('view.saved_book_view.Request.get_int_arg', return_value=mock_page), patch(
            'view.saved_book_view.BookOutputDTO.dump_many', return_value=mock_serialization
        ) as mock_BookOutputDTO_dump_many, patch(
            'view.saved_book_view.PaginationResponse', return_value=mock_json
        ) as mock_PaginationResponse:
            mock_pagination = Mock(Pagination)
            mock_pagination.items = Mock()
            mock_controller.get_all_saved_books = Mock(return_value=mock_pagination)

            result = SavedBookView.get_all_saved_books(mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.get_all_saved_books.assert_called_once_with(mock_page)
            mock_BookOutputDTO_dump_many.assert_called_once_with(mock_pagination.items)
            mock_PaginationResponse.assert_called_once_with(mock_serialization, mock_pagination)
            mock_json.json.assert_called_once()


def test_delete_saved_book(app: Flask, mock_controller: Mock):
    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch(
            'view.saved_book_view.NoContentResponse', return_value=mock_json
        ) as mock_NoContentResponse:
            mock_controller.delete_saved_book = Mock(return_value=None)

            book_id = Mock()
            result = SavedBookView.delete_saved_book(book_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.delete_saved_book.assert_called_once_with(book_id)
            mock_NoContentResponse.assert_called_once_with()
            mock_json.json.assert_called_once()
