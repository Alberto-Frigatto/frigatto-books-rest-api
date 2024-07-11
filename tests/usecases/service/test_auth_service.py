from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask

from app import create_app
from dto.input import LoginInputDTO
from exception import AuthException
from model import User
from repository import IUserRepository
from service.impl import AuthService


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_repository() -> Mock:
    return create_autospec(IUserRepository)


@pytest.fixture
def auth_service(mock_repository: Mock) -> AuthService:
    return AuthService(mock_repository)


@pytest.fixture
def user(app: Flask) -> User:
    with app.app_context():
        return User(
            'frigatto',
            'Senha@123',
            'http://localhost/users/photos/test.jpg',
        )


def test_login_with_valid_credentials(
    auth_service: AuthService, app: Flask, mock_repository: Mock, user: User
):
    with app.app_context():
        with patch(
            'model.user_model.User.check_password', return_value=True
        ) as mock_check_password_hash, patch(
            'flask_jwt_extended.utils.get_current_user', return_value=None
        ), patch(
            'service.impl.auth_service.create_access_token', return_value='new_token'
        ) as mock_create_access_token:
            mock_repository.get_by_username = Mock(return_value=user)

            mock_dto = create_autospec(LoginInputDTO)
            mock_dto.username = 'frigatto'
            mock_dto.password = 'Senha@123'

            result = auth_service.login(mock_dto)

            assert isinstance(result, tuple)

            authenticated_user, token = result

            assert isinstance(authenticated_user, User)
            assert authenticated_user.username == user.username
            assert authenticated_user.password == user.password
            assert authenticated_user.img_url == user.img_url
            assert isinstance(token, str)
            assert token == 'new_token'

            mock_create_access_token.assert_called_once_with(authenticated_user)
            mock_check_password_hash.assert_called_once_with(mock_dto.password)
            mock_repository.get_by_username.assert_called_once_with(mock_dto.username)


def test_when_try_to_login_with_invalid_username_raises_InvalidLogin(
    auth_service: AuthService, app: Flask, mock_repository: Mock
):
    with pytest.raises(AuthException.InvalidLogin), app.app_context():
        with patch('flask_jwt_extended.utils.get_current_user', return_value=None):
            mock_repository.get_by_username = Mock(return_value=None)

            mock_dto = create_autospec(LoginInputDTO)
            mock_dto.username = 'another_username'
            mock_dto.password = 'Senha@123'

            auth_service.login(mock_dto)


def test_when_try_to_login_with_invalid_password_raises_InvalidLogin(
    auth_service: AuthService, app: Flask, mock_repository: Mock, user: User
):
    with pytest.raises(AuthException.InvalidLogin), app.app_context():
        with patch('model.user_model.User.check_password', return_value=False), patch(
            'flask_jwt_extended.utils.get_current_user', return_value=None
        ):
            mock_repository.get_by_username = Mock(return_value=user)

            mock_dto = create_autospec(LoginInputDTO)
            mock_dto.username = 'frigatto'
            mock_dto.password = 'Another_Pwd123'

            auth_service.login(mock_dto)


def test_when_try_to_login_with_user_already_authenticated_raises_UserAlreadyAuthenticated(
    auth_service: AuthService, app: Flask, user: User
):
    with pytest.raises(AuthException.UserAlreadyAuthenticated), app.app_context():
        with patch('flask_jwt_extended.utils.get_current_user', return_value=user):
            mock_dto = create_autospec(LoginInputDTO)
            mock_dto.username = 'frigatto'
            mock_dto.password = 'Another_Pwd123'

            auth_service.login(mock_dto)
