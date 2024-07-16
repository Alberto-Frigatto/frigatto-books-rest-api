from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask

from app import create_app
from db import IDbSession
from exception import UserException
from model import User
from repository.impl import UserRepository


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_db_session() -> Mock:
    return create_autospec(IDbSession)


@pytest.fixture
def user_repository(mock_db_session: Mock) -> UserRepository:
    return UserRepository(mock_db_session)


@pytest.fixture
def user(app: Flask) -> User:
    with app.app_context():
        return User(
            'frigatto',
            'Senha@123',
            'http://localhost/users/photos/test.jpg',
        )


def test_create_user(user_repository: UserRepository, app: Flask, mock_db_session: Mock):
    with app.app_context(), patch(
        'repository.impl.user_repository.UserRepository._user_already_exists',
        return_value=False,
    ):
        mock_user = Mock(User)
        result = user_repository.add(mock_user)

        assert result is None

        mock_db_session.add.assert_called_once_with(mock_user)


def test_when_try_to_create_user_already_exists_raises_UserAlreadyExists(
    user_repository: UserRepository, app: Flask, mock_db_session: Mock, user: User
):
    with app.app_context(), pytest.raises(UserException.UserAlreadyExists):
        mock_db_session.get_one = Mock(return_value=user)

        mock_user = Mock(User)
        user_repository.add(mock_user)


def test_update_user_username(
    user_repository: UserRepository, app: Flask, mock_db_session: Mock, user: User
):
    with app.app_context(), patch(
        'repository.impl.user_repository.UserRepository._user_already_exists',
        return_value=False,
    ):
        mock_db_session.get_one = Mock(return_value=user.username)

        mock_user = Mock(User)
        mock_user.username = 'new_username'

        result = user_repository.update(mock_user)

        assert result is None

        mock_db_session.update.assert_called_once()


def test_when_try_to_update_user_username_to_already_existing_username_raises_UserAlreadyExists(
    user_repository: UserRepository, app: Flask, mock_db_session: Mock
):
    with pytest.raises(UserException.UserAlreadyExists), app.app_context():
        with patch(
            'repository.impl.user_repository.UserRepository._user_already_exists',
            return_value=True,
        ):
            mock_db_session.get_one = Mock(return_value=Mock())

            mock_user = Mock(User)
            mock_user.username = 'frigatto'

            user_repository.update(mock_user)


def test_get_user_by_username_returns_User(
    user_repository: UserRepository, app: Flask, mock_db_session: Mock, user: User
):
    with app.app_context():
        mock_db_session.get_one = Mock(return_value=user)

        result = user_repository.get_by_username(Mock())

        assert isinstance(result, User)
        assert result == user

        mock_db_session.get_one.assert_called_once()


def test_get_user_by_username_returns_None(
    user_repository: UserRepository, app: Flask, mock_db_session: Mock
):
    with app.app_context():
        mock_db_session.get_one = Mock(return_value=None)

        result = user_repository.get_by_username(Mock())

        assert result is None

        mock_db_session.get_one.assert_called_once()


def test_delete_user(user_repository: UserRepository, app: Flask, mock_db_session: Mock):
    with app.app_context(), patch(
        'utils.file.uploader.UserImageUploader.delete', new_callable=Mock()
    ) as mock_UserImageUploader_delete:
        mock_user = Mock(User)
        result = user_repository.delete(mock_user)

        assert result is None

        mock_db_session.delete.assert_called_once_with(mock_user)
        mock_UserImageUploader_delete.assert_called_once_with(mock_user.img_url)
