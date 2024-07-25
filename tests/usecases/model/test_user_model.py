from unittest.mock import Mock, patch

import pytest

from model import User


@pytest.fixture
def user() -> User:
    with patch('model.user_model.generate_password_hash', return_value=Mock()):
        return User(Mock(), Mock(), Mock())


def test_instantiate_User():
    with patch(
        'model.user_model.generate_password_hash', return_value='123'
    ) as mock_generate_password_hash:
        mock_username = Mock()
        mock_password = Mock()
        mock_img_url = Mock()

        user = User(mock_username, mock_password, mock_img_url)

        assert user.id is None
        assert user.username == mock_username
        assert user.password == '123'
        assert user.img_url == mock_img_url

        mock_generate_password_hash.assert_called_once_with(mock_password)


def test_update_User_username(user: User):
    mock_username = Mock()
    user.update_username(mock_username)

    assert user.username == mock_username


def test_update_User_password(user: User):
    with patch(
        'model.user_model.generate_password_hash', return_value='123'
    ) as mock_generate_password_hash:
        mock_password = Mock()
        user.update_password(mock_password)

        assert user.password == '123'

        mock_generate_password_hash.assert_called_once_with(mock_password)


def test_update_User_img_url(user: User):
    mock_img_url = Mock()
    user.update_img_url(mock_img_url)

    assert user.img_url == mock_img_url
