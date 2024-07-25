from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask, Response

from app import create_app
from controller import IBookKeywordController
from dto.input import BookKeywordInputDTO
from model import BookKeyword
from view.book_keyword_view import BookKeywordView


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_controller() -> Mock:
    return create_autospec(IBookKeywordController)


def test_create_book_keyword(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    mock_dto = create_autospec(BookKeywordInputDTO)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch('view.book_keyword_view.BookKeywordInputDTO', return_value=mock_dto), patch(
            'view.book_keyword_view.Request.get_json', return_value={'test': Mock()}
        ) as mock_Request_get_json, patch(
            'view.book_keyword_view.BookKeywordOutputDTO.dump', return_value=mock_serialization
        ) as mock_BookKeywordOutputDTO_dump, patch(
            'view.book_keyword_view.CreatedResponse', return_value=mock_json
        ) as mock_CreatedResponse:
            mock_book_keyword = Mock(BookKeyword)
            mock_controller.create_book_keyword = Mock(return_value=mock_book_keyword)

            book_id = Mock()
            result = BookKeywordView.create_book_keyword(book_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.create_book_keyword.assert_called_once_with(book_id, mock_dto)
            mock_Request_get_json.assert_called_once()
            mock_BookKeywordOutputDTO_dump.assert_called_once_with(mock_book_keyword)
            mock_CreatedResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()


def test_delete_book_keyword(app: Flask, mock_controller: Mock):
    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch(
            'view.book_keyword_view.NoContentResponse', return_value=mock_json
        ) as mock_NoContentResponse:
            mock_controller.delete_book_keyword = Mock(return_value=None)

            book_id = Mock()
            book_keyword_id = Mock()
            result = BookKeywordView.delete_book_keyword(book_id, book_keyword_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.delete_book_keyword.assert_called_once_with(book_id, book_keyword_id)
            mock_NoContentResponse.assert_called_once_with()
            mock_json.json.assert_called_once()
