from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask

from app import create_app
from dto.input import BookKeywordInputDTO
from exception import BookKeywordException
from model import Book, BookKeyword
from repository import IBookKeywordRepository, IBookRepository
from service.impl import BookKeywordService


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_book_keyword_repository() -> Mock:
    return create_autospec(IBookKeywordRepository)


@pytest.fixture
def mock_book_repository() -> Mock:
    return create_autospec(IBookRepository)


@pytest.fixture
def book_keyword_service(
    mock_book_repository: Mock, mock_book_keyword_repository: Mock
) -> BookKeywordService:
    return BookKeywordService(mock_book_repository, mock_book_keyword_repository)


def test_add_book_keyword_to_a_book(
    book_keyword_service: BookKeywordService,
    app: Flask,
    mock_book_repository: Mock,
    mock_book_keyword_repository: Mock,
):
    with app.app_context():
        mock_dto = create_autospec(BookKeywordInputDTO)
        mock_dto.keyword = 'nova palavra chave'

        book_id = '1'

        mock_book = Mock(Book)
        mock_book.id = int(book_id)

        mock_book_repository.get_by_id = Mock(return_value=mock_book)

        result = book_keyword_service.create_book_keyword(book_id, mock_dto)

        mock_book_repository.get_by_id.assert_called_once_with(book_id)
        mock_book_keyword_repository.add.assert_called_once_with(result)

        assert isinstance(result, BookKeyword)
        assert result.id_book == mock_book.id
        assert result.keyword == mock_dto.keyword


def test_delete_book_keyword_from_a_book(
    book_keyword_service: BookKeywordService,
    app: Flask,
    mock_book_repository: Mock,
    mock_book_keyword_repository: Mock,
):
    with app.app_context():
        book_id = '1'

        mock_book = Mock(Book)
        mock_book.id = int(book_id)
        mock_book.book_keywords = [Mock(BookKeyword) for _ in range(3)]

        mock_book_repository.get_by_id = Mock(return_value=mock_book)

        book_keyword_id = '1'

        mock_book_keyword = Mock(BookKeyword)
        mock_book_keyword.id = int(book_keyword_id)
        mock_book_keyword.id_book = mock_book.id

        mock_book_keyword_repository.get_by_id = Mock(return_value=mock_book_keyword)

        result = book_keyword_service.delete_book_keyword(book_id, book_keyword_id)

        mock_book_repository.get_by_id.assert_called_once_with(book_id)
        mock_book_keyword_repository.get_by_id.assert_called_once_with(book_keyword_id)
        mock_book_keyword_repository.delete.assert_called_once_with(mock_book_keyword)

        assert result is None


def test_when_try_to_delete_book_keyword_from_a_book_doesnt_own_this_keyword_raises_BookDoesntOwnThisKeyword(
    book_keyword_service: BookKeywordService,
    app: Flask,
    mock_book_repository: Mock,
    mock_book_keyword_repository: Mock,
):
    with pytest.raises(BookKeywordException.BookDoesntOwnThisKeyword), app.app_context():
        book_id = '1'

        mock_book = Mock(Book)
        mock_book.id = int(book_id)

        mock_book_repository.get_by_id = Mock(return_value=mock_book)

        book_keyword_id = '1'

        mock_book_keyword = Mock(BookKeyword)
        mock_book_keyword.id = int(book_keyword_id)
        mock_book_keyword.id_book = 2

        mock_book_keyword_repository.get_by_id = Mock(return_value=mock_book_keyword)

        book_keyword_service.delete_book_keyword(book_id, book_keyword_id)


def test_when_try_to_delete_the_last_book_keyword_from_a_book_raises_BookMustHaveAtLeastOneKeyword(
    book_keyword_service: BookKeywordService,
    app: Flask,
    mock_book_repository: Mock,
    mock_book_keyword_repository: Mock,
):
    with pytest.raises(BookKeywordException.BookMustHaveAtLeastOneKeyword), app.app_context():
        book_id = '1'

        mock_book = Mock(Book)
        mock_book.id = int(book_id)
        mock_book.book_keywords = [Mock(BookKeyword)]

        mock_book_repository.get_by_id = Mock(return_value=mock_book)

        book_keyword_id = '1'

        mock_book_keyword = Mock(BookKeyword)
        mock_book_keyword.id = int(book_keyword_id)
        mock_book_keyword.id_book = mock_book.id

        mock_book_keyword_repository.get_by_id = Mock(return_value=mock_book_keyword)

        book_keyword_service.delete_book_keyword(book_id, book_keyword_id)
