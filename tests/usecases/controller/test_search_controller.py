from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from controller.impl import SearchController
from dto.input import SearchInputDTO
from model import Book
from service import ISearchService


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_service() -> Mock:
    return create_autospec(ISearchService)


@pytest.fixture
def search_controller(mock_service: Mock) -> SearchController:
    return SearchController(mock_service)


def test_search_books(search_controller: SearchController, app: Flask, mock_service: Mock):
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

        mock_service.search_books = Mock(return_value=mock_pagination)

        page = 1
        mock_dto = create_autospec(SearchInputDTO)

        result = search_controller.search_books(page, mock_dto)

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

        mock_service.search_books.assert_called_once_with(page, mock_dto)
