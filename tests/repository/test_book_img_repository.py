from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask

from app import create_app
from db import IDbSession
from exception import BookImgException
from model import BookImg
from repository.impl import BookImgRepository


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_db_session() -> Mock:
    return create_autospec(IDbSession)


@pytest.fixture
def book_img_repository(mock_db_session: Mock) -> BookImgRepository:
    return BookImgRepository(mock_db_session)


def test_get_book_img_by_id(
    book_img_repository: BookImgRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_book_img = Mock(BookImg)
        mock_db_session.get_by_id = Mock(return_value=mock_book_img)

        book_img_id = '1'
        result = book_img_repository.get_by_id(book_img_id)

        assert isinstance(result, BookImg)
        assert result == mock_book_img

        mock_db_session.get_by_id.assert_called_once_with(BookImg, book_img_id)


def test_when_try_to_get_book_img_does_not_exists_raises_BookImgDoesntExists(
    book_img_repository: BookImgRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context(), pytest.raises(BookImgException.BookImgDoesntExists):
        mock_db_session.get_by_id = Mock(return_value=None)

        book_img_id = '1'
        book_img_repository.get_by_id(book_img_id)


def test_add_book_img(book_img_repository: BookImgRepository, app: Flask, mock_db_session: Mock):
    with app.app_context():
        mock_book_img = Mock(BookImg)

        result = book_img_repository.add(mock_book_img)

        assert result is None

        mock_db_session.add.assert_called_once_with(mock_book_img)


def test_delete_book_img(book_img_repository: BookImgRepository, app: Flask, mock_db_session: Mock):
    with app.app_context(), patch(
        'utils.file.uploader.BookImageUploader.delete', new_callable=Mock()
    ) as mock_BookImageUploader_delete:
        mock_book_img = Mock(BookImg)

        result = book_img_repository.delete(mock_book_img)

        assert result is None

        mock_BookImageUploader_delete.assert_called_once_with(mock_book_img.img_url)
        mock_db_session.delete.assert_called_once_with(mock_book_img)


def test_update_book_img(book_img_repository: BookImgRepository, app: Flask, mock_db_session: Mock):
    with app.app_context():
        result = book_img_repository.update()

        assert result is None

        mock_db_session.update.assert_called_once()
