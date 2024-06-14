import json
import os
import shutil

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from app import create_app
from db import db
from model import User
from schema import users_schema


@pytest.fixture()
def app():
    app = create_app(True)

    with app.app_context():
        db.create_all()

        db.session.execute(
            text(
                f"""
                INSERT INTO users (username, password, img_url)
                    VALUES
                        ('test', '{generate_password_hash('Senha@123')}', 'http://localhost:5000/users/photos/test.jpg'),
                        ('lopes', '{generate_password_hash('Senha@123')}', 'http://localhost:5000/users/photos/test2.jpg')
                """
            )
        )
        db.session.commit()

    yield app

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


def test_instantiate_User():
    username = 'Username_123'
    password = 'SEnha_#45'
    img_url = 'http://localhost:5000/users/photos/test.jpg'

    user = User(username, password, img_url)

    assert user.username == username
    assert user.password != password
    assert user.img_url == img_url


def test_create_user(client: FlaskClient, app: Flask):
    data = {
        'username': 'frigatto',
        'password': 'SEnha#45',
        'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=data)
    response_data = json.loads(response.data)

    assert not response_data['error']
    assert response_data['status'] == 201
    assert response_data['data']
    assert response_data['data']['id'] == 3
    assert response_data['data']['username'] == 'frigatto'
    assert response_data['data']['img_url']
    assert isinstance(response_data['data']['img_url'], str)
    assert response_data['data']['img_url'].startswith('http://localhost:5000/users/photos/')
    assert response_data['data']['img_url'].endswith('.jpg')
    assert response.status_code == 201

    with app.app_context():
        new_user = db.session.get(User, 3)

        assert new_user is not None
        assert new_user.id == 3
        assert new_user.username == 'frigatto'
        assert new_user.password != 'SEnha#45'
        assert new_user.img_url.startswith('http://localhost:5000/users/photos/')
        assert new_user.img_url.endswith('.jpg')


def test_when_try_to_create_user_already_authenticated_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    data = {
        'username': 'frigatto',
        'password': 'SEnha#45',
        'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=data, headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'UserAlreadyAuthenticated'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_create_user_without_data_returns_error_response(client: FlaskClient):
    response = client.post(f'/users')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'NoDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_create_user_with_invalid_data_returns_error_response(client: FlaskClient):
    data = {
        'username': 'frigatto ferreira',
        'password': 'SEnha#45',
        'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    data = {
        'username': 'frigatto',
        'password': 'aaa',
        'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    data = {
        'username': 'frigatto',
        'password': 'aaaEE234',
        'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    data = {
        'username': 'frigatto',
        'password': 'SEnha#45',
        'img': (open('tests/resources/img-11.3mb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    data = {
        'username': 'frigatto',
        'password': 'SEnha#45',
        'img': (open('tests/resources/pdf-2mb.pdf', 'rb'), 'pdf.pdf'),
    }

    response = client.post(f'/users', data=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    data = {'username': 'aaaa'}

    response = client.post(f'/users', data=data, headers={'Content-Type': 'multipart/form-data'})
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    data = {
        'username': 'frigatto',
        'password': 'SEnha#45',
        'img': 'image',
    }

    response = client.post(f'/users', data=data, headers={'Content-Type': 'multipart/form-data'})
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_create_user_already_exists_return_error_reponse(client: FlaskClient):
    data = {
        'username': 'test',
        'password': 'SEnha#45',
        'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
    }

    response = client.post(f'/users', data=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'UserAlreadyExists'
    assert response_data['status'] == 409
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

    assert response_data['error']
    assert response_data['error_name'] == 'ImageNotFound'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_get_user_information(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.get('/users', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': {
            'id': 1,
            'username': 'test',
            'img_url': 'http://localhost:5000/users/photos/test.jpg',
        },
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_get_user_information_without_auth_returns_error_response(client: FlaskClient):
    response = client.get(f'/users')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_get_user_information_with_invalid_auth_returns_error_response(
    client: FlaskClient,
):
    headers = {'Authorization': f'Bearer 123'}

    response = client.get(f'/users', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_update_username(client: FlaskClient, access_token: str, app: Flask):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    updates = {'username': 'andrade'}

    response = client.patch('/users', headers=headers, data=updates)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': {
            'id': 1,
            'username': 'andrade',
            'img_url': 'http://localhost:5000/users/photos/test.jpg',
        },
    }

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        updated_user = db.session.get(User, 1)

        assert updated_user is not None
        assert updated_user.id == 1
        assert updated_user.username == 'andrade'
        assert updated_user.password != 'Senha@123'
        assert updated_user.img_url == 'http://localhost:5000/users/photos/test.jpg'


def test_when_try_to_update_user_without_auth_returns_error_response(client: FlaskClient):
    headers = {'Content-Type': 'multipart/form-data'}

    updates = {'username': 'andrade', 'password': 'Windows#1'}

    response = client.patch('/users', headers=headers, data=updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_update_user_with_invalid_auth_returns_error_response(client: FlaskClient):
    headers = {
        'Content-Type': 'multipart/form-data',
        'Authorization': f'Bearer 123',
    }

    updates = {'username': 'andrade', 'password': 'Windows#1'}

    response = client.patch('/users', headers=headers, data=updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
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

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_updates = {'username': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_updates = {'usernames': 'andrade'}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_updates = {'username': 456}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
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

    assert response_data['error']
    assert response_data['error_name'] == 'UserAlreadyExists'
    assert response_data['status'] == 409
    assert response.status_code == 409


def test_update_password(client: FlaskClient, access_token: str, app: Flask):
    with app.app_context():
        old_user = db.session.get(User, 1)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    updates = {'password': 'Windows#456'}

    response = client.patch('/users', headers=headers, data=updates)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': {
            'id': 1,
            'username': 'test',
            'img_url': 'http://localhost:5000/users/photos/test.jpg',
        },
    }

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        updated_user = db.session.get(User, 1)

        assert updated_user is not None
        assert updated_user.id == 1
        assert updated_user.username == 'test'
        assert old_user is not None
        assert updated_user.password != old_user.password
        assert updated_user.img_url == 'http://localhost:5000/users/photos/test.jpg'


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

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_updates = {'password': 'AndradeFerreira19'}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_updates = {'passwords': 'Windows#456'}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_updates = {'password': 456}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_update_image(client: FlaskClient, app: Flask):
    with app.app_context():
        user = db.session.get(User, 2)
        access_token = create_access_token(user)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    updates = {
        'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
    }

    response = client.patch('/users', headers=headers, data=updates)
    response_data = json.loads(response.data)

    assert not response_data['error']
    assert response_data['status'] == 200
    assert response_data['data']
    assert response_data['data']['id'] == 2
    assert response_data['data']['username'] == 'lopes'
    assert response_data['data']['img_url'] != 'http://localhost:5000/users/photos/test2.jpg'
    assert response.status_code == 200

    with app.app_context():
        updated_user = db.session.get(User, 2)

        assert updated_user is not None
        assert updated_user.id == 2
        assert updated_user.username == 'lopes'
        assert updated_user.password != 'Senha@123'
        assert updated_user.img_url != 'http://localhost:5000/users/photos/test2.jpg'


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

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_updates = {'img': (open('tests/resources/img-11.3mb.png', 'rb'), 'image.png')}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_updates = {'img': 456}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_updates = {'img': (open('tests/resources/pdf-2mb.pdf', 'rb'), 'pdf.pdf')}

    response = client.patch('/users', headers=headers, data=invalid_updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
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

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_update_user_without_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.patch('/users', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'NoDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_dump_User_coming_from_db(app: Flask):
    with app.app_context():
        user = db.session.get(User, 1)

        dump_user = users_schema.dump(user)

        expected_dump_book_genre = {
            'id': 1,
            'username': 'test',
            'img_url': 'http://localhost:5000/users/photos/test.jpg',
        }

        assert dump_user == expected_dump_book_genre