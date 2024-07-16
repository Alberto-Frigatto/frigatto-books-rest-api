import json
import os
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash

from app import create_app
from db import db
from model import User


@pytest.fixture()
def test_app():
    app = create_app(True)

    yield app


@pytest.fixture()
def client(test_app: Flask) -> FlaskClient:
    return test_app.test_client()


def test_when_try_to_request_without_db_connection_returns_error_response():
    app = create_app(False)

    client = app.test_client()
    response = client.post('/bookGenres')
    response_data = json.loads(response.data)

    expected_data = {
        'code': 'DatabaseConnection',
        'message': 'Unable to connect to the database',
        'scope': 'GeneralException',
        'status': 500,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 500


def test_when_try_to_request_with_method_not_allowed_returns_error_response():
    app = create_app(True)

    client = app.test_client()
    response = client.delete('/bookGenres')
    response_data = json.loads(response.data)

    expected_data = {
        'code': 'MethodNotAllowed',
        'message': 'HTTP method not allowed',
        'scope': 'GeneralException',
        'status': 405,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 405


def test_when_try_to_request_an_endpoint_does_not_exists_returns_error_response():
    app = create_app(True)

    client = app.test_client()
    response = client.get('/new_endpoint')
    response_data = json.loads(response.data)

    expected_data = {
        'code': 'EndpointNotFound',
        'message': 'The endpoint does not exist',
        'scope': 'GeneralException',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_when_try_to_request_with_invalid_content_type_returns_error_response(client: FlaskClient):
    headers = {'Content-Type': 'text/html'}
    credentials = {'username': 'test', 'password': 'Senha@123'}

    response = client.post('/auth/login', headers=headers, json=credentials)
    response_data = json.loads(response.data)

    expected_data = {
        'code': 'InvalidContentType',
        'message': 'Invalid Content-Type header',
        'scope': 'GeneralException',
        'status': 415,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 415


def test_request_OPTIONS_HTTP_METHOD(client: FlaskClient):
    response = client.options('/bookGenres')

    assert not response.data
    assert response.status_code == 204
