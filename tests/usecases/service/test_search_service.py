from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from dto.input import SearchInputDTO
from model import Book
from repository import ISearchRepository
from service.impl import SearchService


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_repository() -> Mock:
    return create_autospec(ISearchRepository)


@pytest.fixture
def search_service(mock_repository: Mock) -> SearchService:
    return SearchService(mock_repository)


def test_search_all_books(search_service: SearchService, app: Flask, mock_repository: Mock):
    with app.app_context():
        mock_pagination = Mock(Pagination)
        mock_pagination.items = [Mock(Book) for _ in range(5)]
        mock_pagination.total = len(mock_pagination.items)
        mock_pagination.page = 1
        mock_pagination.pages = 1
        mock_pagination.per_page = 20
        mock_pagination.has_prev = False
        mock_pagination.has_next = False
        mock_pagination.prev_num = None
        mock_pagination.next_num = None

        mock_repository.search = Mock(return_value=mock_pagination)

        mock_dto = create_autospec(SearchInputDTO)
        mock_dto.query = Mock()
        mock_dto.id_book_genre = Mock()
        mock_dto.id_book_kind = Mock()
        mock_dto.release_year = Mock()
        mock_dto.min_price = Mock()
        mock_dto.max_price = Mock()

        page = 1
        result = search_service.search_books(page, mock_dto)

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

        mock_repository.search.assert_called_once_with(
            page=page,
            query=mock_dto.query,
            id_book_genre=mock_dto.id_book_genre,
            id_book_kind=mock_dto.id_book_kind,
            release_year=mock_dto.release_year,
            min_price=mock_dto.min_price,
            max_price=mock_dto.max_price,
        )
