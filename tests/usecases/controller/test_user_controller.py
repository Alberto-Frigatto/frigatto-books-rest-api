from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask

from app import create_app
from controller.impl import UserController
from dto.input import CreateUserInputDTO, UpdateUserInputDTO
from model import User
from service import IUserService


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_service() -> Mock:
    return create_autospec(IUserService)


@pytest.fixture
def user_controller(mock_service: Mock) -> UserController:
    return UserController(mock_service)


def test_get_book_photo(user_controller: UserController, app: Flask, mock_service: Mock):
    with app.app_context():
        mock_file_path = Mock(str)
        mock_mimetype = Mock(str)
        mock_service.get_user_photo = Mock(return_value=(mock_file_path, mock_mimetype))

        mock_file_name = Mock()
        result = user_controller.get_user_photo(mock_file_name)

        assert isinstance(result, tuple)

        file_path, mimetype = result

        assert isinstance(file_path, str)
        assert file_path == mock_file_path
        assert isinstance(mimetype, str)
        assert mimetype == mock_mimetype

        mock_service.get_user_photo.assert_called_once_with(mock_file_name)


def test_create_user(user_controller: UserController, app: Flask, mock_service: Mock):
    with app.app_context():
        mock_user = Mock(User)
        mock_service.create_user = Mock(return_value=mock_user)

        mock_dto = create_autospec(CreateUserInputDTO)

        result = user_controller.create_user(mock_dto)

        assert isinstance(result, User)
        assert result == mock_user

        mock_service.create_user.assert_called_once_with(mock_dto)


def test_get_current_user(user_controller: UserController, app: Flask, mock_service: Mock):
    with app.app_context():
        mock_current_user = Mock(User)
        mock_service.get_current_user = Mock(return_value=mock_current_user)

        result = user_controller.get_current_user()

        assert isinstance(result, User)
        assert result == mock_current_user

        mock_service.get_current_user.assert_called_once()


def test_update_user(user_controller: UserController, app: Flask, mock_service: Mock):
    with app.app_context():
        mock_user = Mock(User)
        mock_service.update_user = Mock(return_value=mock_user)

        mock_dto = create_autospec(CreateUserInputDTO)

        result = user_controller.update_user(mock_dto)

        assert isinstance(result, User)
        assert result == mock_user

        mock_service.update_user.assert_called_once_with(mock_dto)


def test_delete_user(user_controller: UserController, app: Flask, mock_service: Mock):
    with app.app_context():
        result = user_controller.delete_user()

        assert result is None

        mock_service.delete_user.assert_called_once()
