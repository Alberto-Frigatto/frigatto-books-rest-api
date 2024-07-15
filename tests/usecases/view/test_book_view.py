from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask, Response
from flask_sqlalchemy.pagination import Pagination
from werkzeug.datastructures import ImmutableMultiDict

from app import create_app
from controller import IBookController
from dto.input import CreateBookInputDTO, UpdateBookInputDTO
from model import Book
from view.book_view import BookView


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_controller() -> Mock:
    return create_autospec(IBookController)


def test_get_all_books(app: Flask, mock_controller: Mock):
    mock_page = Mock()
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch('view.book_view.Request.get_int_arg', return_value=mock_page), patch(
            'view.book_view.BookOutputDTO.dump_many', return_value=mock_serialization
        ) as mock_BookOutputDTO_dump_many, patch(
            'view.book_view.PaginationResponse', return_value=mock_json
        ) as mock_PaginationResponse:
            mock_pagination = Mock(Pagination)
            mock_pagination.items = Mock()
            mock_controller.get_all_books = Mock(return_value=mock_pagination)

            result = BookView.get_all_books(mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.get_all_books.assert_called_once_with(mock_page)
            mock_BookOutputDTO_dump_many.assert_called_once_with(mock_pagination.items)
            mock_PaginationResponse.assert_called_once_with(mock_serialization, mock_pagination)
            mock_json.json.assert_called_once()


def test_get_book_by_id(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch(
            'view.book_view.BookOutputDTO.dump', return_value=mock_serialization
        ) as mock_BookOutputDTO_dump, patch(
            'view.book_view.OkResponse', return_value=mock_json
        ) as mock_OkResponse:
            mock_book = Mock(Book)
            mock_controller.get_book_by_id = Mock(return_value=mock_book)

            book_id = Mock()
            result = BookView.get_book_by_id(book_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.get_book_by_id.assert_called_once_with(book_id)
            mock_BookOutputDTO_dump.assert_called_once_with(mock_book)
            mock_OkResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()


def test_create_book(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    mock_dto = create_autospec(CreateBookInputDTO)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch('view.book_view.CreateBookInputDTO', return_value=mock_dto), patch(
            'view.book_img_view.Request.get_form', return_value={'test': Mock()}
        ) as mock_Request_get_form, patch(
            'view.book_img_view.Request.get_files', return_value=Mock(ImmutableMultiDict)
        ) as mock_Request_get_files, patch(
            'view.book_view.BookOutputDTO.dump', return_value=mock_serialization
        ) as mock_BookOutputDTO_dump, patch(
            'view.book_view.CreatedResponse', return_value=mock_json
        ) as mock_CreatedResponse:
            mock_book = Mock(Book)
            mock_controller.create_book = Mock(return_value=mock_book)

            result = BookView.create_book(mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.create_book.assert_called_once_with(mock_dto)
            mock_Request_get_form.assert_called_once()
            mock_Request_get_files.assert_called_once()
            mock_BookOutputDTO_dump.assert_called_once_with(mock_book)
            mock_CreatedResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()


def test_delete_book(app: Flask, mock_controller: Mock):
    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch(
            'view.book_view.NoContentResponse', return_value=mock_json
        ) as mock_NoContentResponse:
            mock_controller.delete_book = Mock(return_value=None)

            book_id = Mock()
            result = BookView.delete_book(book_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.delete_book.assert_called_once_with(book_id)
            mock_NoContentResponse.assert_called_once_with()
            mock_json.json.assert_called_once()


def test_update_book(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    mock_dto = create_autospec(UpdateBookInputDTO)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch('view.book_view.UpdateBookInputDTO', return_value=mock_dto), patch(
            'view.book_view.Request.get_form', return_value={'test': Mock()}
        ) as mock_Request_get_form, patch(
            'view.book_view.BookOutputDTO.dump', return_value=mock_serialization
        ) as mock_BookOutputDTO_dump, patch(
            'view.book_view.OkResponse', return_value=mock_json
        ) as mock_OkResponse:
            mock_book = Mock(Book)
            mock_controller.update_book = Mock(return_value=mock_book)

            book_id = Mock()
            result = BookView.update_book(book_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.update_book.assert_called_once_with(book_id, mock_dto)
            mock_Request_get_form.assert_called_once()
            mock_BookOutputDTO_dump.assert_called_once_with(mock_book)
            mock_OkResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()
