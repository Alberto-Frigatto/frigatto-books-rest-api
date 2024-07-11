from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from dto.input import BookGenreInputDTO
from model import BookGenre
from repository import IBookGenreRepository
from service.impl import BookGenreService


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_repository() -> Mock:
    return create_autospec(IBookGenreRepository)


@pytest.fixture
def book_genre_service(mock_repository: Mock) -> BookGenreService:
    return BookGenreService(mock_repository)


def test_get_all_book_genres(
    book_genre_service: BookGenreService, app: Flask, mock_repository: Mock
):
    with app.app_context():
        mock_pagination = Mock(Pagination)
        mock_pagination.items = [Mock(BookGenre) for _ in range(3)]
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
        result = book_genre_service.get_all_book_genres(page)

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


def test_get_book_genre_by_id(
    book_genre_service: BookGenreService, app: Flask, mock_repository: Mock
):
    with app.app_context():
        book_genre_id = '1'

        mock_book_genre = Mock(BookGenre)

        mock_repository.get_by_id = Mock(return_value=mock_book_genre)

        result = book_genre_service.get_book_genre_by_id(book_genre_id)

        assert isinstance(result, BookGenre)
        assert result == mock_book_genre

        mock_repository.get_by_id.assert_called_once_with(book_genre_id)


def test_create_book_genre(book_genre_service: BookGenreService, app: Flask, mock_repository: Mock):
    with app.app_context():
        mock_dto = create_autospec(BookGenreInputDTO)
        mock_dto.genre = 'novo gênero'

        result = book_genre_service.create_book_genre(mock_dto)

        assert isinstance(result, BookGenre)
        assert result.genre == mock_dto.genre

        mock_repository.add.assert_called_once_with(result)


def test_delete_book_genre(book_genre_service: BookGenreService, app: Flask, mock_repository: Mock):
    with app.app_context():
        book_genre_id = '1'

        result = book_genre_service.delete_book_genre(book_genre_id)

        assert result is None

        mock_repository.delete.assert_called_once_with(book_genre_id)


def test_update_book_genre(book_genre_service: BookGenreService, app: Flask, mock_repository: Mock):
    with app.app_context():
        book_genre_id = '1'

        mock_repository.get_by_id = Mock(return_value=BookGenre(Mock()))

        mock_dto = create_autospec(BookGenreInputDTO)
        mock_dto.genre = 'novo gênero'

        result = book_genre_service.update_book_genre(book_genre_id, mock_dto)

        assert isinstance(result, BookGenre)
        assert result.genre == mock_dto.genre

        mock_repository.get_by_id.assert_called_once_with(book_genre_id)
        mock_repository.update.assert_called_once_with(result)
