from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from db import IDbSession
from exception import BookException
from model import Book, BookGenre, BookImg, BookKind
from repository.impl import BookRepository


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_db_session() -> Mock:
    return create_autospec(IDbSession)


@pytest.fixture
def book_repository(mock_db_session: Mock) -> BookRepository:
    return BookRepository(mock_db_session)


def test_get_all_books(book_repository: BookRepository, app: Flask, mock_db_session: Mock):
    with app.app_context():
        mock_pagination = Mock(Pagination)
        mock_pagination.items = [Mock(Book) for _ in range(10)]
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
        result = book_repository.get_all(page)

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


def test_get_book_by_id(book_repository: BookRepository, app: Flask, mock_db_session: Mock):
    with app.app_context():
        mock_book = Mock(Book)
        mock_db_session.get_by_id = Mock(return_value=mock_book)

        book_id = '1'
        result = book_repository.get_by_id(book_id)

        assert isinstance(result, Book)
        assert result == mock_book

        mock_db_session.get_by_id.assert_called_once_with(Book, book_id)


def test_when_try_to_get_book_by_id_from_book_does_not_exists_raises_BookDoesntExists(
    book_repository: BookRepository, app: Flask, mock_db_session: Mock
):
    with pytest.raises(BookException.BookDoesntExists), app.app_context():
        mock_db_session.get_by_id = Mock(return_value=None)

        book_id = '1'
        book_repository.get_by_id(book_id)


def test_create_book(book_repository: BookRepository, app: Flask, mock_db_session: Mock):
    with app.app_context():
        mock_db_session.get_one = Mock(return_value=None)

        mock_book = Mock(Book)
        result = book_repository.add(mock_book)

        assert result is None

        mock_db_session.get_one.assert_called_once()
        mock_db_session.add.assert_called_once_with(mock_book)


def test_when_try_to_create_book_already_exists_raises_BookAlreadyExists(
    book_repository: BookRepository, app: Flask, mock_db_session: Mock
):
    with pytest.raises(BookException.BookAlreadyExists), app.app_context():
        mock_db_session.get_one = Mock(return_value=Mock(Book))

        book_repository.add(Mock(Book))


def test_delete_book(book_repository: BookRepository, app: Flask, mock_db_session: Mock):
    with app.app_context(), patch(
        'repository.impl.book_repository.BookImageUploader.delete', new_callable=Mock()
    ) as mock_BookImageUploader_delete:
        mock_book = Mock(Book)

        mock_book_img = Mock(BookImg)
        mock_book_img.img_url = Mock()

        mock_book.book_imgs = [mock_book_img for _ in range(4)]

        mock_db_session.get_by_id = Mock(return_value=mock_book)

        book_id = '1'
        result = book_repository.delete(book_id)

        assert result is None

        for book_img in mock_book.book_imgs:
            mock_BookImageUploader_delete.assert_called_with(book_img.img_url)

        mock_db_session.get_by_id.assert_called_once_with(Book, book_id)
        mock_db_session.delete.assert_called_once()


def test_update_book_name(book_repository: BookRepository, app: Flask, mock_db_session: Mock):
    with app.app_context(), patch(
        'repository.impl.book_repository.BookRepository._book_already_exists', return_value=False
    ) as mock_BookRepository_book_already_exists:
        mock_db_session.get_one = Mock(return_value=Mock(Book))

        mock_book = Mock(Book)
        mock_book.name = 'Outro Nome'
        result = book_repository.update(mock_book)

        assert result is None

        mock_BookRepository_book_already_exists.assert_called_once_with(mock_book)
        mock_db_session.get_one.assert_called_once()
        mock_db_session.update.assert_called_once()


def test_update_other_book_attrs_without_name(
    book_repository: BookRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context(), patch(
        'repository.impl.book_repository.BookRepository._book_already_exists', return_value=False
    ) as mock_BookRepository_book_already_exists:
        mock_db_session.get_one = Mock(return_value=None)

        mock_book = Mock(Book)
        result = book_repository.update(mock_book)

        assert result is None

        mock_BookRepository_book_already_exists.assert_called_once_with(mock_book)
        mock_db_session.get_one.assert_called_once()
        mock_db_session.update.assert_called_once()


def test_when_try_to_update_book_with_name_from_book_already_exists_raises_BookAlreadyExists(
    book_repository: BookRepository, app: Flask, mock_db_session: Mock
):
    with pytest.raises(BookException.BookAlreadyExists), app.app_context():
        with patch(
            'repository.impl.book_repository.BookRepository._book_already_exists',
            return_value=True,
        ):
            mock_db_session.get_one = Mock(return_value=None)

            mock_book = Mock(Book)
            book_repository.update(mock_book)
