import json
import os
import shutil
from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from app import create_app
from db import db
from model import User


@pytest.fixture()
def app():
    app = create_app(True)

    with app.app_context():
        db.create_all()

        db.session.execute(
            text(
                "INSERT INTO users (username, password, img_url) VALUES (:username, :password, :img_url)"
            ),
            [
                {
                    'username': 'test',
                    'password': generate_password_hash('Senha@123'),
                    'img_url': 'http://localhost:5000/users/photos/test.jpg',
                },
                {
                    'username': 'lopes',
                    'password': generate_password_hash('Senha@123'),
                    'img_url': 'http://localhost:5000/users/photos/test2.jpg',
                },
            ],
        )
        db.session.commit()

    yield app

    clean_uploads()


def clean_uploads():
    dir = 'tests/uploads/'

    for file in os.listdir(dir):
        path = os.path.join(dir, file)

        if file != 'test.jpg':
            os.remove(path)

    if not os.path.exists('tests/uploads/test2.jpg'):
        shutil.copyfile('tests/resources/img-417kb.png', 'tests/uploads/test2.jpg')


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def access_token(app: Flask) -> str:
    with app.app_context():
        user = db.session.get(User, 1)
        return create_access_token(user)


def test_create_user(client: FlaskClient, app: Flask):
    data_for_create = {
        'username': 'frigatto',
        'password': 'SEnha#45',
        'img': (open('tests/resources/img-417kb.png', 'rb'), 'image.png'),
    }

    response = client.post('/users', data=data_for_create)
    response_data: dict = json.loads(response.data)

    new_user_id = 3
    expected_data = {'id': new_user_id, 'username': 'frigatto'}

    assert response_data['id'] == new_user_id
    assert response_data['username'] == expected_data['username']
    assert response_data['img_url']
    assert isinstance(response_data['img_url'], str)
    assert response_data['img_url'].startswith('http://localhost:5000/users/photos/')
    assert response_data['img_url'].endswith('.jpg')
    assert response.status_code == 201

    with app.app_context():
        new_user = db.session.get(User, new_user_id)

        assert new_user is not None
        assert new_user.id == new_user_id
        assert new_user.username == expected_data['username']
        assert new_user.password != data_for_create['password']
        assert new_user.img_url.startswith('http://localhost:5000/users/photos/')
        assert new_user.img_url.endswith('.jpg')

    dir = 'tests/uploads'
    for filename in os.listdir(dir):
        if filename not in ('test.jpg', 'test2.jpg'):
            assert os.path.isfile(os.path.join(dir, filename))


def test_when_try_to_create_user_already_authenticated_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    data = {
        'username': 'frigatto',
        'password': 'SEnha#45',
        'img': (open('tests/resources/img-417kb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=data, headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'AuthException',
        'code': 'UserAlreadyAuthenticated',
        'message': 'The user is already logged in',
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_user_without_data_returns_error_response(client: FlaskClient):
    response = client.post(f'/users')
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'NoDataSent',
        'message': 'No data sent',
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_user_with_invalid_username_returns_error_response(client: FlaskClient):
    invalid_data = {
        'username': 'frigatto ferreira',
        'password': 'SEnha#45',
        'img': (open('tests/resources/img-417kb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['username'],
                'msg': "String should match pattern '^[a-zA-Z\\d_-]+$'",
                'type': 'string_pattern_mismatch',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {
        'username': 'abc',
        'password': 'SEnha#45',
        'img': (open('tests/resources/img-417kb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['username'],
                'msg': 'String should have at least 4 characters',
                'type': 'string_too_short',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {
        'username': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'password': 'SEnha#45',
        'img': (open('tests/resources/img-417kb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['username'],
                'msg': 'String should have at most 50 characters',
                'type': 'string_too_long',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {
        'username': 'frigatto(*&#@$)',
        'password': 'SEnha#45',
        'img': (open('tests/resources/img-417kb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['username'],
                'msg': "String should match pattern '^[a-zA-Z\\d_-]+$'",
                'type': 'string_pattern_mismatch',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_user_with_invalid_password_returns_error_response(client: FlaskClient):
    invalid_data = {
        'username': 'frigatto',
        'password': 'aaa',
        'img': (open('tests/resources/img-417kb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['password'],
                'msg': 'Value error, The provided password should have at least 8 characters',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {
        'username': 'frigatto',
        'password': 'aaaEE123',
        'img': (open('tests/resources/img-417kb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['password'],
                'msg': 'Value error, The provided password has not the necessary chars',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {
        'username': 'frigatto',
        'password': 'eE2@',
        'img': (open('tests/resources/img-417kb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['password'],
                'msg': 'Value error, The provided password should have at least 8 characters',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {
        'username': 'frigatto',
        'password': 'eE2@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'img': (open('tests/resources/img-417kb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['password'],
                'msg': 'Value error, The provided password should have at most 255 characters',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_user_with_invalid_img_returns_error_response(client: FlaskClient):
    invalid_data = {
        'username': 'frigatto',
        'password': 'SEnha#45',
        'img': (open('tests/resources/img-11.3mb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['img'],
                'msg': 'Value error, The provided image is larger than 5MB',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {
        'username': 'frigatto',
        'password': 'SEnha#45',
        'img': (open('tests/resources/pdf-2mb.pdf', 'rb'), 'pdf.pdf'),
    }

    response = client.post(f'/users', data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['img'],
                'msg': 'Value error, The provided file is not an image',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {
        'username': 'frigatto',
        'password': 'SEnha#45',
        'img': 'image',
    }

    response = client.post(
        f'/users', data=invalid_data, headers={'Content-Type': 'multipart/form-data'}
    )
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['img'],
                'msg': 'Value error, The provided image is not a file',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_user_with_invalid_data_returns_error_response(client: FlaskClient):
    invalid_data = {'username': 'aaaa'}

    response = client.post(
        f'/users', data=invalid_data, headers={'Content-Type': 'multipart/form-data'}
    )
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['password'], 'msg': 'Field required', 'type': 'missing'},
            {'loc': ['img'], 'msg': 'Field required', 'type': 'missing'},
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {'username': 'frigatto', 'passwords': 'sss'}

    response = client.post(
        f'/users', data=invalid_data, headers={'Content-Type': 'multipart/form-data'}
    )
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['password'], 'msg': 'Field required', 'type': 'missing'},
            {'loc': ['img'], 'msg': 'Field required', 'type': 'missing'},
            {
                'loc': ['passwords'],
                'msg': 'Extra inputs are not permitted',
                'type': 'extra_forbidden',
            },
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_user_already_exists_return_error_reponse(client: FlaskClient):
    data = {
        'username': 'test',
        'password': 'SEnha#45',
        'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'UserException',
        'code': 'UserAlreadyExists',
        'message': 'This user already exists',
        'status': 409,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409

    data = {
        'username': ' tESt   ',
        'password': 'SEnha#45',
        'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=data)
    response_data = json.loads(response.data)

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409


def test_get_user_image(client: FlaskClient):
    filename = 'test.jpg'

    response = client.get(f'/users/photos/{filename}')

    assert response.mimetype == 'image/jpeg'
    assert response.content_type == 'image/jpeg'
    assert response.content_length
    assert response.status_code == 200


def test_when_try_to_get_user_image_with_invalid_filename_returns_error_response(
    client: FlaskClient,
):
    filename = 'cat.jpg'

    response = client.get(f'/users/photos/{filename}')
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'ImageException',
        'code': 'ImageNotFound',
        'message': f'The image {filename} was not found',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_get_user_information(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.get('/users', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'id': 1,
        'username': 'test',
        'img_url': 'http://localhost:5000/users/photos/test.jpg',
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_get_user_information_without_auth_returns_error_response(client: FlaskClient):
    response = client.get(f'/users')
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'SecurityException',
        'code': 'MissingJWT',
        'message': 'JWT token not provided',
        'status': 401,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 401


def test_when_try_to_get_user_information_with_invalid_auth_returns_error_response(
    client: FlaskClient,
):
    headers = {'Authorization': f'Bearer 123'}

    response = client.get(f'/users', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'SecurityException',
        'code': 'InvalidJWT',
        'message': 'Invalid JWT token',
        'status': 401,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 401


def test_update_username(client: FlaskClient, access_token: str, app: Flask):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    updates = {'username': 'andrade'}

    response = client.patch('/users', headers=headers, data=updates)
    response_data = json.loads(response.data)

    updated_user_id = 1
    expected_data = {
        'id': updated_user_id,
        'username': 'andrade',
        'img_url': 'http://localhost:5000/users/photos/test.jpg',
    }

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        updated_user = db.session.get(User, updated_user_id)

        assert updated_user is not None
        assert updated_user.id == updated_user_id
        assert updated_user.username == expected_data['username']

        original_password = 'Senha@123'
        assert updated_user.password != original_password
        assert updated_user.img_url == expected_data['img_url']


def test_when_try_to_update_user_without_auth_returns_error_response(client: FlaskClient):
    headers = {'Content-Type': 'multipart/form-data'}

    updates = {'username': 'andrade', 'password': 'Windows#1'}

    response = client.patch('/users', headers=headers, data=updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'SecurityException',
        'code': 'MissingJWT',
        'message': 'JWT token not provided',
        'status': 401,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 401


def test_when_try_to_update_user_with_invalid_auth_returns_error_response(client: FlaskClient):
    headers = {
        'Content-Type': 'multipart/form-data',
        'Authorization': f'Bearer 123',
    }

    updates = {'username': 'andrade', 'password': 'Windows#1'}

    response = client.patch('/users', headers=headers, data=updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'SecurityException',
        'code': 'InvalidJWT',
        'message': 'Invalid JWT token',
        'status': 401,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 401


def test_when_try_to_update_username_with_invalid_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    invalid_updates = {'username': 'andrade ferreira'}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['username'],
                'msg': "String should match pattern '^[a-zA-Z\\d_-]+$'",
                'type': 'string_pattern_mismatch',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_updates = {'username': 'abc'}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['username'],
                'msg': 'String should have at least 4 characters',
                'type': 'string_too_short',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_updates = {'username': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['username'],
                'msg': 'String should have at most 50 characters',
                'type': 'string_too_long',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_updates = {'username': 'frigatto(*&#@$)'}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['username'],
                'msg': "String should match pattern '^[a-zA-Z\\d_-]+$'",
                'type': 'string_pattern_mismatch',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_updates = {'usernames': 'andrade'}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['usernames'],
                'msg': 'Extra inputs are not permitted',
                'type': 'extra_forbidden',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_update_username_to_username_already_exists_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    updates = {'username': 'lopes'}

    response = client.patch('/users', headers=headers, data=updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'UserException',
        'code': 'UserAlreadyExists',
        'message': 'This user already exists',
        'status': 409,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409


def test_update_password(client: FlaskClient, access_token: str, app: Flask):
    user_id = 1

    with app.app_context():
        old_user = db.session.get(User, user_id)
        assert old_user is not None

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    updates = {'password': 'Windows#456'}

    response = client.patch('/users', headers=headers, data=updates)
    response_data = json.loads(response.data)

    expected_data = {
        'id': user_id,
        'username': 'test',
        'img_url': 'http://localhost:5000/users/photos/test.jpg',
    }

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        updated_user = db.session.get(User, user_id)

        assert updated_user is not None
        assert updated_user.id == user_id
        assert updated_user.username == expected_data['username']
        assert updated_user.password != old_user.password
        assert updated_user.img_url == expected_data['img_url']


def test_when_try_to_update_password_with_invalid_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    invalid_updates = {'password': 'andradeasd'}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['password'],
                'msg': 'Value error, The provided password has not the necessary chars',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_updates = {'password': 'AndradeFerreira19'}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['password'],
                'msg': 'Value error, The provided password has not the necessary chars',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_updates = {'passwords': 'Windows#456'}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['passwords'],
                'msg': 'Extra inputs are not permitted',
                'type': 'extra_forbidden',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_updates = {'password': '456'}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['password'],
                'msg': 'Value error, The provided password should have at least 8 characters',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_updates = {
        'password': 'eE2@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    }

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['password'],
                'msg': 'Value error, The provided password should have at most 255 characters',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_update_image(client: FlaskClient, app: Flask):
    user_id = 2

    with app.app_context():
        user = db.session.get(User, user_id)
        access_token = create_access_token(user)
        assert user is not None

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    updates = {
        'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
    }

    response = client.patch('/users', headers=headers, data=updates)
    response_data = json.loads(response.data)

    expected_data = {'id': user_id, 'username': 'lopes'}

    assert response_data['id'] == user_id
    assert response_data['username'] == expected_data['username']
    assert response_data['img_url']
    assert isinstance(response_data['img_url'], str)
    assert response_data['img_url'].startswith('http://localhost:5000/users/photos/')
    assert response_data['img_url'].endswith('.jpg')

    original_img_url = 'http://localhost:5000/users/photos/test2.jpg'
    assert response_data['img_url'] != original_img_url
    assert response.status_code == 200

    with app.app_context():
        updated_user = db.session.get(User, user_id)

        assert updated_user is not None
        assert updated_user.id == user_id
        assert updated_user.username == expected_data['username']
        original_password = 'Senha@123'
        assert updated_user.password != original_password
        assert updated_user.img_url != original_img_url
        assert updated_user.img_url.startswith('http://localhost:5000/users/photos/')
        assert updated_user.img_url.endswith('.jpg')

    dir = 'tests/uploads'

    assert 'test2.jpg' not in os.listdir(dir)

    for filename in os.listdir(dir):
        if filename != 'test.jpg':
            assert os.path.isfile(os.path.join(dir, filename))


def test_when_try_to_update_image_with_invalid_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    invalid_updates = {'img': 'andradeasd'}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['img'],
                'msg': 'Value error, The provided image is not a file',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_updates = {'img': (open('tests/resources/img-11.3mb.png', 'rb'), 'image.png')}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['img'],
                'msg': 'Value error, The provided image is larger than 5MB',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_updates = {'img': 456}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['img'],
                'msg': 'Value error, The provided image is not a file',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_updates = {'img': (open('tests/resources/pdf-2mb.pdf', 'rb'), 'pdf.pdf')}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['img'],
                'msg': 'Value error, The provided file is not an image',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_update_user_with_invalid_data_returns_errror_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    updates = {
        'username': 'andrade',
        'aa': 'aoihdwa',
        'imgs': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
    }

    response = client.patch('/users', headers=headers, data=updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['aa'], 'msg': 'Extra inputs are not permitted', 'type': 'extra_forbidden'},
            {'loc': ['imgs'], 'msg': 'Extra inputs are not permitted', 'type': 'extra_forbidden'},
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_update_user_without_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.patch('/users', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'NoDataSent',
        'message': 'No data sent',
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400
