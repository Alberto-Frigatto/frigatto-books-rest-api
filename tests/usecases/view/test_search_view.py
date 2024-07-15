from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask, Response
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from controller import ISearchController
from dto.input import SearchInputDTO
from view.search_view import SearchView


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_controller() -> Mock:
    return create_autospec(ISearchController)


def test_search_books(app: Flask, mock_controller: Mock):
    mock_page = Mock()
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    mock_dto = create_autospec(SearchInputDTO)

    with app.app_context():
        with patch('view.search_view.SearchInputDTO', return_value=mock_dto), patch(
            'view.search_view.Request.get_json', return_value={'test': Mock()}
        ) as mock_Request_get_json, patch(
            'view.search_view.Request.get_int_arg', return_value=mock_page
        ), patch(
            'view.search_view.BookOutputDTO.dump_many', return_value=mock_serialization
        ) as mock_BookOutputDTO_dump_many, patch(
            'view.search_view.PaginationResponse', return_value=mock_json
        ) as mock_PaginationResponse:
            mock_pagination = Mock(Pagination)
            mock_pagination.items = Mock()
            mock_controller.search_books = Mock(return_value=mock_pagination)

            result = SearchView.search_books(mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.search_books.assert_called_once_with(mock_page, mock_dto)
            mock_Request_get_json.assert_called_once()
            mock_BookOutputDTO_dump_many.assert_called_once_with(mock_pagination.items)
            mock_PaginationResponse.assert_called_once_with(mock_serialization, mock_pagination)
            mock_json.json.assert_called_once()
