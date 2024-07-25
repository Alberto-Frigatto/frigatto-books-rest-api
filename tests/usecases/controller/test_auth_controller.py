from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask

from app import create_app
from controller.impl import AuthController
from dto.input import LoginInputDTO
from model import User
from service import IAuthService


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_service() -> Mock:
    return create_autospec(IAuthService)


@pytest.fixture
def auth_controller(mock_service: Mock) -> AuthController:
    return AuthController(mock_service)


def test_login_with_valid_credentials(
    auth_controller: AuthController, app: Flask, mock_service: Mock
):
    with app.app_context():
        mock_user, mock_token = Mock(User), Mock(str)
        mock_service.login = Mock(return_value=(mock_user, mock_token))

        mock_dto = create_autospec(LoginInputDTO)

        result = auth_controller.login(mock_dto)

        assert isinstance(result, tuple)

        user, token = result

        assert isinstance(user, User)
        assert user == mock_user
        assert isinstance(token, str)
        assert token == mock_token

        mock_service.login.assert_called_once_with(mock_dto)
