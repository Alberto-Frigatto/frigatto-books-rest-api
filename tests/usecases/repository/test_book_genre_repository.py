from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from db import IDbSession
from exception import BookGenreException
from model import Book, BookGenre
from repository.impl import BookGenreRepository


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_db_session() -> Mock:
    return create_autospec(IDbSession)


@pytest.fixture
def book_genre_repository(mock_db_session: Mock) -> BookGenreRepository:
    return BookGenreRepository(mock_db_session)


def test_get_all_book_genres(
    book_genre_repository: BookGenreRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_pagination = Mock(Pagination)
        mock_pagination.items = [Mock(BookGenre) for _ in range(10)]
        mock_pagination.total = len(mock_pagination.items)
        mock_pagination.page = 1
        mock_pagination.pages = 1
        mock_pagination.per_page = 20
        mock_pagination.has_prev = False
        mock_pagination.has_next = False
        mock_pagination.prev_num = None
        mock_pagination.next_num = None

        mock_db_session.paginate = Mock(return_value=mock_pagination)

        page = 1
        result = book_genre_repository.get_all(page)

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

        mock_db_session.paginate.assert_called_once()


def test_get_book_genre_by_id(
    book_genre_repository: BookGenreRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_book_genre = Mock(BookGenre)
        mock_db_session.get_by_id = Mock(return_value=mock_book_genre)

        book_genre_id = '1'
        result = book_genre_repository.get_by_id(book_genre_id)

        assert isinstance(result, BookGenre)
        assert result == mock_book_genre

        mock_db_session.get_by_id.assert_called_once_with(BookGenre, book_genre_id)


def test_when_try_to_get_book_genre_by_id_from_book_genre_does_not_exists_raises_BookGenreDoesntExists(
    book_genre_repository: BookGenreRepository, app: Flask, mock_db_session: Mock
):
    with pytest.raises(BookGenreException.BookGenreDoesntExists), app.app_context():
        mock_db_session.get_by_id = Mock(return_value=None)

        book_genre_id = '1'
        book_genre_repository.get_by_id(book_genre_id)


def test_create_book_genre(
    book_genre_repository: BookGenreRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_db_session.get_one = Mock(return_value=None)

        mock_book_genre = Mock(BookGenre)
        result = book_genre_repository.add(mock_book_genre)

        assert result is None

        mock_db_session.get_one.assert_called_once()
        mock_db_session.add.assert_called_once_with(mock_book_genre)


def test_when_try_to_create_book_genre_already_exists_raises_BookGenreAlreadyExists(
    book_genre_repository: BookGenreRepository, app: Flask, mock_db_session: Mock
):
    with pytest.raises(BookGenreException.BookGenreAlreadyExists), app.app_context():
        mock_db_session.get_one = Mock(return_value=Mock(BookGenre))

        book_genre_repository.add(Mock(BookGenre))


def test_delete_book_genre(
    book_genre_repository: BookGenreRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_book_genre = Mock(BookGenre)
        mock_db_session.get_by_id = Mock(return_value=mock_book_genre)
        mock_db_session.get_many = Mock(return_value=None)

        book_genre_id = '1'
        result = book_genre_repository.delete(book_genre_id)

        assert result is None

        mock_db_session.get_many.assert_called_once()
        mock_db_session.get_by_id.assert_called_once_with(BookGenre, book_genre_id)
        mock_db_session.delete.assert_called_once()


def test_when_try_to_delete_book_genre_with_linked_books_raises_ThereAreLinkedBooksWithThisBookGenre(
    book_genre_repository: BookGenreRepository, app: Flask, mock_db_session: Mock
):
    with pytest.raises(BookGenreException.ThereAreLinkedBooksWithThisBookGenre), app.app_context():
        mock_db_session.get_by_id = Mock(return_value=Mock(BookGenre))
        mock_db_session.get_many = Mock(return_value=[Mock(Book) for _ in range(2)])

        book_genre_id = '1'
        book_genre_repository.delete(book_genre_id)


def test_update_book_genre(
    book_genre_repository: BookGenreRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_db_session.get_one = Mock(return_value=None)

        mock_book_genre = Mock(BookGenre)
        result = book_genre_repository.update(mock_book_genre)

        assert result is None

        mock_db_session.get_one.assert_called_once()
        mock_db_session.update.assert_called_once()


def test_when_try_to_update_book_genre_with_genre_already_exists_raises_BookGenreAlreadyExists(
    book_genre_repository: BookGenreRepository, app: Flask, mock_db_session: Mock
):
    with pytest.raises(BookGenreException.BookGenreAlreadyExists), app.app_context():
        mock_db_session.get_one = Mock(return_value=Mock(BookGenre))

        book_genre_repository.update(Mock(BookGenre))
