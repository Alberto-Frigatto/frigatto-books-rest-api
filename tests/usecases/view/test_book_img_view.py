from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask, Response
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from controller import IBookImgController
from dto.input import BookImgInputDTO
from model import BookImg
from view.book_img_view import BookImgView


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_controller() -> Mock:
    return create_autospec(IBookImgController)


def test_get_book_img_by_filename(app: Flask, mock_controller: Mock):
    mock_response = Mock(Response)

    with app.app_context():
        with patch('view.book_img_view.send_file', return_value=mock_response):
            mock_controller.get_book_photo = Mock(return_value=(str(Mock()), str(Mock())))

            filename = Mock()
            result = BookImgView.get_book_img_by_filename(filename, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.get_book_photo.assert_called_once_with(filename)


def test_add_book_img(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    mock_dto = create_autospec(BookImgInputDTO)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch('view.book_img_view.BookImgInputDTO', return_value=mock_dto), patch(
            'view.book_img_view.Request.get_form', return_value={'test': Mock()}
        ) as mock_Request_get_form, patch(
            'view.book_img_view.Request.get_files', return_value={'test2': Mock()}
        ) as mock_Request_get_files, patch(
            'view.book_img_view.BookImgOutputDTO.dump', return_value=mock_serialization
        ) as mock_BookImgOutputDTO_dump, patch(
            'view.book_img_view.CreatedResponse', return_value=mock_json
        ) as mock_CreatedResponse:
            mock_book_img = Mock(BookImg)
            mock_controller.create_book_img = Mock(return_value=mock_book_img)

            book_id = Mock()
            result = BookImgView.add_book_img(book_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.create_book_img.assert_called_once_with(book_id, mock_dto)
            mock_Request_get_form.assert_called_once()
            mock_Request_get_files.assert_called_once()
            mock_BookImgOutputDTO_dump.assert_called_once_with(mock_book_img)
            mock_CreatedResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()


def test_update_book_img(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    mock_dto = create_autospec(BookImgInputDTO)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch('view.book_img_view.BookImgInputDTO', return_value=mock_dto), patch(
            'view.book_img_view.Request.get_form', return_value={'test': Mock()}
        ) as mock_Request_get_form, patch(
            'view.book_img_view.Request.get_files', return_value={'test2': Mock()}
        ) as mock_Request_get_files, patch(
            'view.book_img_view.BookImgOutputDTO.dump', return_value=mock_serialization
        ) as mock_BookImgOutputDTO_dump, patch(
            'view.book_img_view.OkResponse', return_value=mock_json
        ) as mock_OkResponse:
            mock_book_img = Mock(BookImg)
            mock_controller.update_book_img = Mock(return_value=mock_book_img)

            book_id = Mock()
            book_img_id = Mock()
            result = BookImgView.update_book_img(book_id, book_img_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.update_book_img.assert_called_once_with(book_id, book_img_id, mock_dto)
            mock_Request_get_form.assert_called_once()
            mock_Request_get_files.assert_called_once()
            mock_BookImgOutputDTO_dump.assert_called_once_with(mock_book_img)
            mock_OkResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()


def test_delete_book_img(app: Flask, mock_controller: Mock):
    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch(
            'view.book_img_view.NoContentResponse', return_value=mock_json
        ) as mock_NoContentResponse:
            mock_controller.delete_book_img = Mock(return_value=None)

            book_id = Mock()
            book_img_id = Mock()
            result = BookImgView.delete_book_img(book_id, book_img_id, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.delete_book_img.assert_called_once_with(book_id, book_img_id)
            mock_NoContentResponse.assert_called_once_with()
            mock_json.json.assert_called_once()
