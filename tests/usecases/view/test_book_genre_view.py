from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask, Response
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from controller import IBookGenreController
from dto.input import BookGenreInputDTO
from model import BookGenre
from view.book_genre_view import BookGenreView


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_controller() -> Mock:
    return create_autospec(IBookGenreController)


def test_get_all_book_genres(app: Flask, mock_controller: Mock):
    mock_page = Mock()
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch('view.book_genre_view.Request.get_int_arg', return_value=mock_page), patch(
            'view.book_genre_view.BookGenreOutputDTO.dump_many', return_value=mock_serialization
        ) as mock_BookGenreOutputDTO_dump_many, patch(
            'view.book_genre_view.PaginationResponse', return_value=mock_json
        ) as mock_PaginationResponse:
            mock_pagination = Mock(Pagination)
            mock_pagination.items = Mock()
            mock_controller.get_all_book_genres = Mock(return_value=mock_pagination)

            result = BookGenreView.get_all_book_genres(mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.get_all_book_genres.assert_called_once_with(mock_page)
            mock_BookGenreOutputDTO_dump_many.assert_called_once_with(mock_pagination.items)
            mock_PaginationResponse.assert_called_once_with(mock_serialization, mock_pagination)
            mock_json.json.assert_called_once()


def test_get_book_genre_by_id(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch(
            'view.book_genre_view.BookGenreOutputDTO.dump', return_value=mock_serialization
        ) as mock_BookGenreOutputDTO_dump, patch(
            'view.book_genre_view.OkResponse', return_value=mock_json
        ) as mock_OkResponse:
            mock_book_genre = Mock(BookGenre)
            mock_controller.get_book_genre_by_id = Mock(return_value=mock_book_genre)

            book_genre_id = Mock()
            result = BookGenreView.get_book_genre_by_id(book_genre_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.get_book_genre_by_id.assert_called_once_with(book_genre_id)
            mock_BookGenreOutputDTO_dump.assert_called_once_with(mock_book_genre)
            mock_OkResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()


def test_create_book_genre(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    mock_dto = create_autospec(BookGenreInputDTO)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch('view.book_genre_view.BookGenreInputDTO', return_value=mock_dto), patch(
            'view.book_genre_view.Request.get_json', return_value={'test': Mock()}
        ) as mock_Request_get_json, patch(
            'view.book_genre_view.BookGenreOutputDTO.dump', return_value=mock_serialization
        ) as mock_BookGenreOutputDTO_dump, patch(
            'view.book_genre_view.CreatedResponse', return_value=mock_json
        ) as mock_CreatedResponse:
            mock_book_genre = Mock(BookGenre)
            mock_controller.create_book_genre = Mock(return_value=mock_book_genre)

            result = BookGenreView.create_book_genre(mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.create_book_genre.assert_called_once_with(mock_dto)
            mock_Request_get_json.assert_called_once()
            mock_BookGenreOutputDTO_dump.assert_called_once_with(mock_book_genre)
            mock_CreatedResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()


def test_delete_book_genre(app: Flask, mock_controller: Mock):
    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch(
            'view.book_genre_view.NoContentResponse', return_value=mock_json
        ) as mock_NoContentResponse:
            mock_controller.delete_book_genre = Mock(return_value=None)

            book_genre_id = Mock()
            result = BookGenreView.delete_book_genre(book_genre_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.delete_book_genre.assert_called_once_with(book_genre_id)
            mock_NoContentResponse.assert_called_once_with()
            mock_json.json.assert_called_once()


def test_update_book_genre(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    mock_dto = create_autospec(BookGenreInputDTO)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch('view.book_genre_view.BookGenreInputDTO', return_value=mock_dto), patch(
            'view.book_genre_view.Request.get_json', return_value={'test': Mock()}
        ) as mock_Request_get_json, patch(
            'view.book_genre_view.BookGenreOutputDTO.dump', return_value=mock_serialization
        ) as mock_BookGenreOutputDTO_dump, patch(
            'view.book_genre_view.OkResponse', return_value=mock_json
        ) as mock_OkResponse:
            mock_book_genre = Mock(BookGenre)
            mock_controller.update_book_genre = Mock(return_value=mock_book_genre)

            book_genre_id = Mock()
            result = BookGenreView.update_book_genre(book_genre_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.update_book_genre.assert_called_once_with(book_genre_id, mock_dto)
            mock_Request_get_json.assert_called_once()
            mock_BookGenreOutputDTO_dump.assert_called_once_with(mock_book_genre)
            mock_OkResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()
