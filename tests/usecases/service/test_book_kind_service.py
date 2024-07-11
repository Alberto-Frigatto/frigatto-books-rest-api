from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from dto.input import BookKindInputDTO
from model import BookKind
from repository import IBookKindRepository
from service.impl import BookKindService


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_repository() -> Mock:
    return create_autospec(IBookKindRepository)


@pytest.fixture
def book_kind_service(mock_repository: Mock) -> BookKindService:
    return BookKindService(mock_repository)


def test_get_all_book_kinds(book_kind_service: BookKindService, app: Flask, mock_repository: Mock):
    with app.app_context():
        mock_pagination = Mock(Pagination)
        mock_pagination.items = [Mock(BookKind) for _ in range(3)]
        mock_pagination.total = len(mock_pagination.items)
        mock_pagination.page = 1
        mock_pagination.pages = 1
        mock_pagination.per_page = 20
        mock_pagination.has_prev = False
        mock_pagination.has_next = False
        mock_pagination.prev_num = None
        mock_pagination.next_num = None

        mock_repository.get_all = Mock(return_value=mock_pagination)

        page = 1
        result = book_kind_service.get_all_book_kinds(page)

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

        mock_repository.get_all.assert_called_once_with(page)


def test_get_book_kind_by_id(book_kind_service: BookKindService, app: Flask, mock_repository: Mock):
    with app.app_context():
        book_kind_id = '1'

        mock_book_kind = Mock(BookKind)

        mock_repository.get_by_id = Mock(return_value=mock_book_kind)

        result = book_kind_service.get_book_kind_by_id(book_kind_id)

        assert isinstance(result, BookKind)
        assert result == mock_book_kind

        mock_repository.get_by_id.assert_called_once_with(book_kind_id)


def test_create_book_kind(book_kind_service: BookKindService, app: Flask, mock_repository: Mock):
    with app.app_context():
        mock_dto = create_autospec(BookKindInputDTO)
        mock_dto.kind = 'novo tipo'

        result = book_kind_service.create_book_kind(mock_dto)

        assert isinstance(result, BookKind)
        assert result.kind == mock_dto.kind

        mock_repository.add.assert_called_once_with(result)


def test_delete_book_kind(book_kind_service: BookKindService, app: Flask, mock_repository: Mock):
    with app.app_context():
        book_kind_id = '1'

        result = book_kind_service.delete_book_kind(book_kind_id)

        assert result is None

        mock_repository.delete.assert_called_once_with(book_kind_id)


def test_update_book_kind(book_kind_service: BookKindService, app: Flask, mock_repository: Mock):
    with app.app_context():
        book_kind_id = '1'

        mock_repository.get_by_id = Mock(return_value=BookKind(Mock()))

        mock_dto = create_autospec(BookKindInputDTO)
        mock_dto.kind = 'novo tipo'

        result = book_kind_service.update_book_kind(book_kind_id, mock_dto)

        assert isinstance(result, BookKind)
        assert result.kind == mock_dto.kind

        mock_repository.get_by_id.assert_called_once_with(book_kind_id)
        mock_repository.update.assert_called_once_with(result)
