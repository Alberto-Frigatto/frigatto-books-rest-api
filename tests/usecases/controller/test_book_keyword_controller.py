from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask

from app import create_app
from controller.impl import BookKeywordController
from dto.input import BookKeywordInputDTO
from model import BookKeyword
from service import IBookKeywordService


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_service() -> Mock:
    return create_autospec(IBookKeywordService)


@pytest.fixture
def book_keyword_controller(mock_service: Mock) -> BookKeywordController:
    return BookKeywordController(mock_service)


def test_create_book_keyword(
    book_keyword_controller: BookKeywordController, app: Flask, mock_service: Mock
):
    with app.app_context():
        mock_book_keyword = Mock(BookKeyword)
        mock_service.create_book_keyword = Mock(return_value=mock_book_keyword)

        mock_dto = create_autospec(BookKeywordInputDTO)
        book_id = '1'

        result = book_keyword_controller.create_book_keyword(book_id, mock_dto)

        assert isinstance(result, BookKeyword)
        assert result == mock_book_keyword

        mock_service.create_book_keyword.assert_called_once_with(book_id, mock_dto)


def test_delete_book_keyword(
    book_keyword_controller: BookKeywordController, app: Flask, mock_service: Mock
):
    with app.app_context():
        book_id = '1'
        book_keyword_id = '1'

        result = book_keyword_controller.delete_book_keyword(book_id, book_keyword_id)

        assert result is None

        mock_service.delete_book_keyword.assert_called_once_with(book_id, book_keyword_id)
