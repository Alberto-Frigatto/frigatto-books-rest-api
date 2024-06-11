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

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidContentType'
    assert response_data['status'] == 415
    assert response.status_code == 415


def test_when_try_to_login_with_already_authenticated_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    credentials = {'username': 'teste', 'password': 'Senha@123'}

    response = client.post(f'/auth/login', headers=headers, json=credentials)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'UserAlreadyAuthenticated'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_login_with_invalid_username_returns_error_response(client: FlaskClient):
    credentials = {'username': 'teste', 'password': 'Senha@123'}

    response = client.post(f'/auth/login', json=credentials)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidLogin'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_login_with_invalid_password_returns_error_response(client: FlaskClient):
    credentials = {'username': 'test', 'password': 'Senha@1234'}

    response = client.post(f'/auth/login', json=credentials)
    response_data = json.loads(response.data)
    assert response_data['error']
    assert response_data['error_name'] == 'InvalidLogin'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_login_with_invalid_data_returns_error_response(client: FlaskClient):
    credentials = {'usernames': 'test', 'passwords': 'Senha@123'}

    response = client.post(f'/auth/login', json=credentials)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_login_without_data_returns_error_response(client: FlaskClient):
    response = client.post(f'/auth/login')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'NoDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_logout(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.post('/auth/logout', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {'error': False, 'status': 200}

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_logout_without_auth_returns_error_response(client: FlaskClient):
    response = client.post(f'/auth/logout')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_logout_with_invalid_auth_returns_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.post(f'/auth/logout', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401
