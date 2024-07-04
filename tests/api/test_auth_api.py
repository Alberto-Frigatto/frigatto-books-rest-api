import json

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


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def access_token(app: Flask) -> str:
    with app.app_context():
        user = db.session.get(User, 1)
        return create_access_token(user)


def test_login_with_valid_credentials(client: FlaskClient):
    credentials = {'username': 'test', 'password': 'Senha@123'}

    response = client.post(f'/auth/login', json=credentials)
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


def test_when_try_to_login_with_content_type_multipart_form_data_returns_error_response(
    client: FlaskClient,
):
    headers = {'Content-Type': 'multipart/form-data'}
    credentials = {'username': 'test', 'password': 'Senha@123'}

    response = client.post(f'/auth/login', headers=headers, data=credentials)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'InvalidContentType',
        'message': 'Invalid Content-Type header',
        'status': 415,
    }

    assert response_data == expected_data
    assert response.status_code == 415


def test_when_try_to_login_with_already_authenticated_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    credentials = {'username': 'teste', 'password': 'Senha@123'}

    response = client.post(f'/auth/login', headers=headers, json=credentials)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'UserAlreadyAuthenticated',
        'message': 'The user is already logged in',
        'status': 400,
    }

    assert response_data == expected_data
    assert response.status_code == 400


def test_when_try_to_login_with_invalid_username_returns_error_response(client: FlaskClient):
    credentials = {'username': 'teste', 'password': 'Senha@123'}

    response = client.post(f'/auth/login', json=credentials)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'InvalidLogin',
        'message': 'Invalid username or password',
        'status': 401,
    }

    assert response_data == expected_data
    assert response.status_code == 401


def test_when_try_to_login_with_invalid_password_returns_error_response(client: FlaskClient):
    credentials = {'username': 'test', 'password': 'Senha@1234'}

    response = client.post(f'/auth/login', json=credentials)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'InvalidLogin',
        'message': 'Invalid username or password',
        'status': 401,
    }

    assert response_data == expected_data
    assert response.status_code == 401


def test_when_try_to_login_with_invalid_data_returns_error_response(client: FlaskClient):
    credentials = {'usernames': 'test', 'passwords': 'Senha@123'}

    response = client.post(f'/auth/login', json=credentials)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'InvalidDataSent',
        'message': [
            {'loc': ['username'], 'msg': 'Field required', 'type': 'missing'},
            {'loc': ['password'], 'msg': 'Field required', 'type': 'missing'},
            {
                'loc': ['passwords'],
                'msg': 'Extra inputs are not permitted',
                'type': 'extra_forbidden',
            },
            {
                'loc': ['usernames'],
                'msg': 'Extra inputs are not permitted',
                'type': 'extra_forbidden',
            },
        ],
        'status': 400,
    }

    assert response_data == expected_data
    assert response.status_code == 400


def test_when_try_to_login_without_data_returns_error_response(client: FlaskClient):
    response = client.post(f'/auth/login')
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'NoDataSent',
        'message': 'No data sent',
        'status': 400,
    }

    assert response_data == expected_data
    assert response.status_code == 400


def test_logout(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.post('/auth/logout', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_logout_without_auth(client: FlaskClient):
    response = client.post(f'/auth/logout')
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
    }

    assert response_data == expected_data
    assert response.status_code == 200
