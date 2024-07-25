from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask, Response

from app import create_app
from controller import IAuthController
from dto.input import LoginInputDTO
from model import User
from view.auth_view import AuthView


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_controller() -> Mock:
    return create_autospec(IAuthController)


def test_login(app: Flask, mock_controller: Mock):
    mock_serialization = Mock()

    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    mock_dto = create_autospec(LoginInputDTO)

    with app.app_context():
        with patch(
            'flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=Mock()
        ), patch('view.auth_view.set_access_cookies') as mock_set_access_cookies, patch(
            'view.auth_view.LoginInputDTO', return_value=mock_dto
        ), patch(
            'view.book_genre_view.Request.get_json', return_value={'test': Mock()}
        ) as mock_Request_get_json, patch(
            'view.auth_view.UserOutputDTO.dump', return_value=mock_serialization
        ) as mock_UserOutputDTO_dump, patch(
            'view.auth_view.OkResponse', return_value=mock_json
        ) as mock_OkResponse:
            mock_user = Mock(User)
            mock_token = str(Mock())
            mock_controller.login = Mock(return_value=(mock_user, mock_token))

            result = AuthView.login(mock_controller)

            assert isinstance(result, Response)
            assert result == mock_response

            mock_controller.login.assert_called_once_with(mock_dto)
            mock_set_access_cookies.assert_called_once_with(mock_response, mock_token)
            mock_Request_get_json.assert_called_once()
            mock_UserOutputDTO_dump.assert_called_once_with(mock_user)
            mock_OkResponse.assert_called_once_with(mock_serialization)
            mock_json.json.assert_called_once()


def test_logout(app: Flask):
    mock_json = Mock()
    mock_response = Mock(Response)
    mock_json.json = Mock(return_value=mock_response)

    with app.app_context():
        with patch('view.auth_view.unset_jwt_cookies') as mock_unset_jwt_cookies, patch(
            'view.auth_view.NoContentResponse', return_value=mock_json
        ) as mock_NoContentResponse:
            result = AuthView.logout()

            assert isinstance(result, Response)
            assert result == mock_response

            mock_unset_jwt_cookies.assert_called_once_with(mock_response)
            mock_NoContentResponse.assert_called_once()
            mock_json.json.assert_called_once()
