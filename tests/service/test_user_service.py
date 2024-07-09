from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask

from app import create_app
from dto.input import CreateUserInputDTO, UpdateUserInputDTO
from exception import AuthException, ImageException
from model import User
from repository import IUserRepository
from service.impl import UserService
from utils.file.uploader import UserImageUploader


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_repository() -> Mock:
    return create_autospec(IUserRepository)


@pytest.fixture
def user_service(mock_repository: Mock) -> UserService:
    return UserService(mock_repository)


@pytest.fixture
def user(app: Flask) -> User:
    with app.app_context():
        return User(
            'frigatto',
            'Senha@123',
            'http://localhost/users/photos/test.jpg',
        )


def test_create_user(user_service: UserService, app: Flask, mock_repository: Mock):
    with app.app_context():
        with patch(
            'model.user_model.generate_password_hash', return_value='123'
        ) as mock_generate_password_hash, patch(
            'flask_jwt_extended.utils.get_current_user', return_value=None
        ):
            mock_dto = create_autospec(CreateUserInputDTO)
            mock_dto.username = 'lopes_gustavo'
            mock_dto.password = 'Senha@123'
            mock_dto.img = create_autospec(UserImageUploader)
            mock_dto.img.get_url = Mock(return_value='http://localhost/users/photos/new_image.jpg')

            result = user_service.create_user(mock_dto)

            mock_generate_password_hash.assert_called_once_with(mock_dto.password)
            mock_dto.img.save.assert_called_once()
            mock_dto.img.get_url.assert_called_once()
            mock_repository.add.assert_called_once_with(result)

            assert isinstance(result, User)
            assert result.username == mock_dto.username
            assert result.password == '123'
            assert result.img_url == mock_dto.img.get_url()


def test_when_try_to_create_user_when_user_is_already_logged_in_raises_UserAlreadyAuthenticated(
    user_service: UserService,
    app: Flask,
    user: User,
):
    with pytest.raises(AuthException.UserAlreadyAuthenticated):
        with app.app_context():
            with patch('flask_jwt_extended.utils.get_current_user', return_value=user):
                mock_dto = create_autospec(CreateUserInputDTO)

                user_service.create_user(mock_dto)


def test_get_current_user(
    user_service: UserService,
    app: Flask,
    user: User,
):
    with app.app_context():
        with patch('flask_jwt_extended.utils.get_current_user', return_value=user):
            result = user_service.get_current_user()

            assert isinstance(result, User)
            assert result == user


def test_get_user_photo(
    user_service: UserService,
    app: Flask,
):
    with app.app_context():
        result = user_service.get_user_photo('test.jpg')

        assert isinstance(result, tuple)

        file_path, mimetype = result

        assert file_path == 'tests/uploads/test.jpg'
        assert mimetype == 'image/jpeg'


def test_when_try_to_get_user_photo_with_filename_does_not_exists_raises_ImageNotFound(
    user_service: UserService,
    app: Flask,
):
    with pytest.raises(ImageException.ImageNotFound):
        with app.app_context():
            user_service.get_user_photo('image_doesnt_exists.jpg')


def test_update_username(user_service: UserService, app: Flask, mock_repository: Mock, user: User):
    with app.app_context():
        with patch('flask_jwt_extended.utils.get_current_user', return_value=user):
            mock_dto = create_autospec(UpdateUserInputDTO)
            mock_dto.username = 'lopes_gustavo'
            mock_dto.img = None
            mock_dto.items = {
                'username': mock_dto.username,
                'password': None,
                'img': mock_dto.img,
            }.items()

            result = user_service.update_user(mock_dto)

            assert isinstance(result, User)
            assert result.username == mock_dto.username
            assert result.password == user.password
            assert result.img_url == user.img_url

            mock_repository.update.assert_called_once_with(result)


def test_update_password(user_service: UserService, app: Flask, mock_repository: Mock, user: User):
    with app.app_context():
        with patch(
            'model.user_model.generate_password_hash', return_value='123'
        ) as mock_generate_password_hash, patch(
            'flask_jwt_extended.utils.get_current_user', return_value=user
        ):
            mock_dto = create_autospec(UpdateUserInputDTO)
            mock_dto.password = 'Nova senha'
            mock_dto.img = None
            mock_dto.items = {
                'username': None,
                'password': mock_dto.password,
                'img': mock_dto.img,
            }.items()

            result = user_service.update_user(mock_dto)

            assert isinstance(result, User)
            assert result.username == user.username
            assert result.password == '123'
            assert result.img_url == user.img_url

            mock_generate_password_hash.assert_called_once_with(mock_dto.password)
            mock_repository.update.assert_called_once_with(result)


def test_update_image(user_service: UserService, app: Flask, mock_repository: Mock, user: User):
    with app.app_context():
        with patch(
            'utils.file.uploader.UserImageUploader.delete', new_callable=Mock()
        ) as mock_UserImageUploader_delete, patch(
            'flask_jwt_extended.utils.get_current_user', return_value=user
        ):
            mock_dto = create_autospec(UpdateUserInputDTO)
            mock_dto.img = create_autospec(UserImageUploader)
            mock_dto.img.get_url = Mock(return_value='http://localhost/users/photos/new_image.jpg')
            mock_dto.items = {
                'username': None,
                'password': None,
                'img': mock_dto.img,
            }.items()

            result = user_service.update_user(mock_dto)

            mock_UserImageUploader_delete.assert_called_once_with(
                'http://localhost/users/photos/test.jpg'
            )
            mock_dto.img.save.assert_called_once()
            mock_dto.img.get_url.assert_called_once()
            mock_repository.update.assert_called_once_with(result)

            assert isinstance(result, User)
            assert result.username == user.username
            assert result.password == user.password
            assert result.img_url == mock_dto.img.get_url()
