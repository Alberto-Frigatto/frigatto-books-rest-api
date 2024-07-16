from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask, Response

from app import create_app
from controller import IUserController
from dto.input import CreateUserInputDTO, UpdateUserInputDTO
from model import User
from view.user_view import UserView


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_controller() -> Mock:
    return create_autospec(IUserController)


def test_get_user_info(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch(
            'view.user_view.UserOutputDTO.dump', return_value=mock_serialization
        ) as mock_UserOutputDTO_dump, patch(
            'view.user_view.OkResponse', return_value=mock_json
        ) as mock_OkResponse:
            mock_user = Mock(User)
            mock_controller.get_current_user = Mock(return_value=mock_user)

            result = UserView.get_user_info(mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.get_current_user.assert_called_once()
            mock_UserOutputDTO_dump.assert_called_once_with(mock_user)
            mock_OkResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()


def test_create_user(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    mock_dto = create_autospec(CreateUserInputDTO)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch('view.user_view.CreateUserInputDTO', return_value=mock_dto), patch(
            'view.user_view.Request.get_form', return_value={'test': Mock()}
        ) as mock_Request_get_form, patch(
            'view.user_view.Request.get_files', return_value={'test2': Mock()}
        ) as mock_Request_get_files, patch(
            'view.user_view.UserOutputDTO.dump', return_value=mock_serialization
        ) as mock_UserOutputDTO_dump, patch(
            'view.user_view.CreatedResponse', return_value=mock_json
        ) as mock_CreatedResponse:
            mock_user = Mock(User)
            mock_controller.create_user = Mock(return_value=mock_user)

            result = UserView.create_user(mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.create_user.assert_called_once_with(mock_dto)
            mock_Request_get_form.assert_called_once()
            mock_Request_get_files.assert_called_once()
            mock_UserOutputDTO_dump.assert_called_once_with(mock_user)
            mock_CreatedResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()


def test_update_user(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    mock_dto = create_autospec(UpdateUserInputDTO)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch('view.user_view.UpdateUserInputDTO', return_value=mock_dto), patch(
            'view.user_view.Request.get_form', return_value={'test': Mock()}
        ) as mock_Request_get_form, patch(
            'view.user_view.Request.get_files', return_value={'test2': Mock()}
        ) as mock_Request_get_files, patch(
            'view.user_view.UserOutputDTO.dump', return_value=mock_serialization
        ) as mock_UserOutputDTO_dump, patch(
            'view.user_view.OkResponse', return_value=mock_json
        ) as mock_OkResponse:
            mock_user = Mock(User)
            mock_controller.update_user = Mock(return_value=mock_user)

            result = UserView.update_user(mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.update_user.assert_called_once_with(mock_dto)
            mock_Request_get_form.assert_called_once()
            mock_Request_get_files.assert_called_once()
            mock_UserOutputDTO_dump.assert_called_once_with(mock_user)
            mock_OkResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()


def test_get_user_photo(app: Flask, mock_controller: Mock):
    mock_response = Mock(Response)

    with app.app_context():
        with patch('view.user_view.send_file', return_value=mock_response):
            mock_controller.get_user_photo = Mock(return_value=(str(Mock()), str(Mock())))

            filename = Mock()
            result = UserView.get_user_photo(filename, mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.get_user_photo.assert_called_once_with(filename)


def test_delete_user(app: Flask, mock_controller: Mock):
    mock_response = Mock(Response)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch('view.user_view.redirect', return_value=mock_response) as mock_redirect, patch(
            'view.user_view.url_for', return_value=Mock()
        ):
            mock_controller.delete_user = Mock(return_value=None)

            result = UserView.delete_user(mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.delete_user.assert_called_once()
            mock_redirect.assert_called_once()
