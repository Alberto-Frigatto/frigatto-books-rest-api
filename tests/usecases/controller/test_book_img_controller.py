from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask

from app import create_app
from controller.impl import BookImgController
from dto.input import BookImgInputDTO
from model import BookImg
from service import IBookImgService


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_service() -> Mock:
    return create_autospec(IBookImgService)


@pytest.fixture
def book_img_controller(mock_service: Mock) -> BookImgController:
    return BookImgController(mock_service)


def test_get_book_photo(book_img_controller: BookImgController, app: Flask, mock_service: Mock):
    with app.app_context():
        mock_file_path = Mock(str)
        mock_mimetype = Mock(str)
        mock_service.get_book_photo = Mock(return_value=(mock_file_path, mock_mimetype))

        mock_file_name = Mock()
        result = book_img_controller.get_book_photo(mock_file_name)

        assert isinstance(result, tuple)

        file_path, mimetype = result

        assert isinstance(file_path, str)
        assert file_path == mock_file_path
        assert isinstance(mimetype, str)
        assert mimetype == mock_mimetype

        mock_service.get_book_photo.assert_called_once_with(mock_file_name)


def test_create_book_img(book_img_controller: BookImgController, app: Flask, mock_service: Mock):
    with app.app_context():
        mock_book_img = Mock(BookImg)
        mock_service.create_book_img = Mock(return_value=mock_book_img)

        mock_dto = create_autospec(BookImgInputDTO)
        book_id = '1'

        result = book_img_controller.create_book_img(book_id, mock_dto)

        assert isinstance(result, BookImg)
        assert result == mock_book_img

        mock_service.create_book_img.assert_called_once_with(book_id, mock_dto)


def test_delete_book_img(book_img_controller: BookImgController, app: Flask, mock_service: Mock):
    with app.app_context():
        book_id = '1'
        book_img_id = '1'

        result = book_img_controller.delete_book_img(book_id, book_img_id)

        assert result is None

        mock_service.delete_book_img.assert_called_once_with(book_id, book_img_id)


def test_update_book_img(book_img_controller: BookImgController, app: Flask, mock_service: Mock):
    with app.app_context():
        mock_book_img = Mock(BookImg)
        mock_service.update_book_img = Mock(return_value=mock_book_img)

        book_id = '1'
        book_img_id = '1'
        mock_dto = create_autospec(BookImgInputDTO)

        result = book_img_controller.update_book_img(book_id, book_img_id, mock_dto)

        assert isinstance(result, BookImg)
        assert result == mock_book_img

        mock_service.update_book_img.assert_called_once_with(book_id, book_img_id, mock_dto)
