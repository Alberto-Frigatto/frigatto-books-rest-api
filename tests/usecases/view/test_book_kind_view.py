from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask, Response
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from controller import IBookKindController
from dto.input import BookKindInputDTO
from model import BookKind
from view.book_kind_view import BookKindView


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_controller() -> Mock:
    return create_autospec(IBookKindController)


def test_get_all_book_kinds(app: Flask, mock_controller: Mock):
    mock_page = Mock()
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch('view.book_kind_view.Request.get_int_arg', return_value=mock_page), patch(
            'view.book_kind_view.BookKindOutputDTO.dump_many', return_value=mock_serialization
        ) as mock_BookKindOutputDTO_dump_many, patch(
            'view.book_kind_view.PaginationResponse', return_value=mock_json
        ) as mock_PaginationResponse:
            mock_pagination = Mock(Pagination)
            mock_pagination.items = Mock()
            mock_controller.get_all_book_kinds = Mock(return_value=mock_pagination)

            result = BookKindView.get_all_book_kinds(mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.get_all_book_kinds.assert_called_once_with(mock_page)
            mock_BookKindOutputDTO_dump_many.assert_called_once_with(mock_pagination.items)
            mock_PaginationResponse.assert_called_once_with(mock_serialization, mock_pagination)
            mock_json.json.assert_called_once()


def test_get_book_kind_by_id(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch(
            'view.book_kind_view.BookKindOutputDTO.dump', return_value=mock_serialization
        ) as mock_BookKindOutputDTO_dump, patch(
            'view.book_kind_view.OkResponse', return_value=mock_json
        ) as mock_OkResponse:
            mock_book_kind = Mock(BookKind)
            mock_controller.get_book_kind_by_id = Mock(return_value=mock_book_kind)

            book_kind_id = Mock()
            result = BookKindView.get_book_kind_by_id(book_kind_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.get_book_kind_by_id.assert_called_once_with(book_kind_id)
            mock_BookKindOutputDTO_dump.assert_called_once_with(mock_book_kind)
            mock_OkResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()


def test_create_book_kind(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    mock_dto = create_autospec(BookKindInputDTO)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch(
            'view.book_kind_view.BookKindInputDTO', return_value=mock_dto
        ) as mock_BookKindInputDTO, patch(
            'view.book_kind_view.Request.get_json', return_value={'test': Mock()}
        ) as mock_Request_get_json, patch(
            'view.book_kind_view.BookKindOutputDTO.dump', return_value=mock_serialization
        ) as mock_BookKindOutputDTO_dump, patch(
            'view.book_kind_view.CreatedResponse', return_value=mock_json
        ) as mock_CreatedResponse:
            mock_book_kind = Mock(BookKind)
            mock_controller.create_book_kind = Mock(return_value=mock_book_kind)

            result = BookKindView.create_book_kind(mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.create_book_kind.assert_called_once_with(mock_dto)
            mock_Request_get_json.assert_called_once()
            mock_BookKindOutputDTO_dump.assert_called_once_with(mock_book_kind)
            mock_CreatedResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()


def test_delete_book_kind(app: Flask, mock_controller: Mock):
    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch(
            'view.book_kind_view.NoContentResponse', return_value=mock_json
        ) as mock_NoContentResponse:
            mock_controller.delete_book_kind = Mock(return_value=None)

            book_kind_id = Mock()
            result = BookKindView.delete_book_kind(book_kind_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.delete_book_kind.assert_called_once_with(book_kind_id)
            mock_NoContentResponse.assert_called_once_with()
            mock_json.json.assert_called_once()


def test_update_book_kind(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    mock_dto = create_autospec(BookKindInputDTO)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch(
            'view.book_kind_view.BookKindInputDTO', return_value=mock_dto
        ) as mock_BookKindInputDTO, patch(
            'view.book_kind_view.Request.get_json', return_value={'test': Mock()}
        ) as mock_Request_get_json, patch(
            'view.book_kind_view.BookKindOutputDTO.dump', return_value=mock_serialization
        ) as mock_BookKindOutputDTO_dump, patch(
            'view.book_kind_view.OkResponse', return_value=mock_json
        ) as mock_OkResponse:
            mock_book_kind = Mock(BookKind)
            mock_controller.update_book_kind = Mock(return_value=mock_book_kind)

            book_kind_id = Mock()
            result = BookKindView.update_book_kind(book_kind_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.update_book_kind.assert_called_once_with(book_kind_id, mock_dto)
            mock_Request_get_json.assert_called_once()
            mock_BookKindOutputDTO_dump.assert_called_once_with(mock_book_kind)
            mock_OkResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()
