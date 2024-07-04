import json

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from app import create_app
from db import db
from model import BookKeyword, User


@pytest.fixture()
def app():
    app = create_app(True)

    with app.app_context():
        db.create_all()

        db.session.execute(
            text(
                "INSERT INTO users (username, password, img_url) VALUES (:username, :password, :img_url)"
            ),
            {
                'username': 'test',
                'password': generate_password_hash('Senha@123'),
                'img_url': 'http://localhost:5000/users/photos/test.jpg',
            },
        )

        db.session.execute(
            text("INSERT INTO book_genres (genre) VALUES (:genre)"), {'genre': 'fábula'}
        )
        db.session.execute(text("INSERT INTO book_kinds (kind) VALUES (:kind)"), {'kind': 'físico'})

        db.session.execute(
            text(
                """--sql
                INSERT INTO books
                    (name, price, author, release_year, id_kind, id_genre)
                    VALUES (:name, :price, :author, :release_year, :id_kind, :id_genre)
                """
            ),
            [
                {
                    'name': 'O Pequeno Príncipe',
                    'price': 10.99,
                    'author': 'Antoine de Saint Exupéry',
                    'release_year': 1943,
                    'id_kind': 1,
                    'id_genre': 1,
                },
                {
                    'name': 'O Poderoso Chefão',
                    'price': 20.99,
                    'author': 'Mario Puzo',
                    'release_year': 1969,
                    'id_kind': 1,
                    'id_genre': 1,
                },
            ],
        )

        db.session.execute(
            text("INSERT INTO book_keywords (keyword, id_book) VALUES (:keyword, :id_book)"),
            [
                {'keyword': 'dramático', 'id_book': 1},
                {'keyword': 'infantil', 'id_book': 1},
                {'keyword': 'máfia', 'id_book': 2},
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


def test_instantiate_BookKeyword():
    keyword = 'palavra chave'
    book_keyword = BookKeyword(keyword)

    assert book_keyword.keyword == keyword


def test_add_book_keyword_in_lowercase(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1
    data = {'keyword': 'emocionante'}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=data)
    response_data = json.loads(response.data)

    new_keyword_id = 4
    expected_data = {
        'error': False,
        'status': 201,
        'data': {'id': new_keyword_id, 'keyword': data['keyword']},
    }

    assert response_data == expected_data
    assert response.status_code == 201

    with app.app_context():
        book_keyword = db.session.get(BookKeyword, new_keyword_id)

        assert book_keyword is not None
        assert book_keyword.id == new_keyword_id
        assert book_keyword.keyword == data['keyword']
        assert book_keyword.id_book == book_id


def test_add_book_keyword_with_space_and_in_uppercase(
    client: FlaskClient, access_token: str, app: Flask
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1
    data = {'keyword': ' MUITO EMOCIONANTE'}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=data)
    response_data = json.loads(response.data)

    new_keyword_id = 4
    expected_data = {
        'error': False,
        'status': 201,
        'data': {'id': new_keyword_id, 'keyword': data['keyword'].lower().strip()},
    }

    assert response_data == expected_data
    assert response.status_code == 201

    with app.app_context():
        book_keyword = db.session.get(BookKeyword, new_keyword_id)

        assert book_keyword is not None
        assert book_keyword.id == new_keyword_id
        assert book_keyword.keyword == data['keyword'].lower().strip()
        assert book_keyword.id_book == book_id


def test_when_try_to_add_book_keyword_with_invalid_data(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1

    invalid_data = {'keyword': ''}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'InvalidDataSent',
        'message': [
            {
                'loc': ['keyword'],
                'msg': 'String should have at least 3 characters',
                'type': 'string_too_short',
            }
        ],
        'status': 400,
    }

    assert response_data == expected_data
    assert response.status_code == 400

    invalid_data = {'keyword': '  '}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'InvalidDataSent',
        'message': [
            {
                'loc': ['keyword'],
                'msg': 'String should have at least 3 characters',
                'type': 'string_too_short',
            }
        ],
        'status': 400,
    }

    assert response_data == expected_data
    assert response.status_code == 400

    invalid_data = {'keyword': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'InvalidDataSent',
        'message': [
            {
                'loc': ['keyword'],
                'msg': 'String should have at most 20 characters',
                'type': 'string_too_long',
            }
        ],
        'status': 400,
    }

    assert response_data == expected_data
    assert response.status_code == 400

    invalid_data = {'keyword': 'adwa234@#$@#$as'}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'InvalidDataSent',
        'message': [
            {
                'loc': ['keyword'],
                'msg': "String should match pattern '^[a-zA-ZÀ-ÿç\\s\\d]+$'",
                'type': 'string_pattern_mismatch',
            }
        ],
        'status': 400,
    }

    assert response_data == expected_data
    assert response.status_code == 400

    invalid_data = {'keyword': 456}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'InvalidDataSent',
        'message': [
            {'loc': ['keyword'], 'msg': 'Input should be a valid string', 'type': 'string_type'}
        ],
        'status': 400,
    }

    assert response_data == expected_data
    assert response.status_code == 400

    invalid_data = {'keywords': 'teste'}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'InvalidDataSent',
        'message': [
            {'loc': ['keyword'], 'msg': 'Field required', 'type': 'missing'},
            {
                'loc': ['keywords'],
                'msg': 'Extra inputs are not permitted',
                'type': 'extra_forbidden',
            },
        ],
        'status': 400,
    }

    assert response_data == expected_data
    assert response.status_code == 400


def test_when_try_to_add_book_keyword_without_data(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1

    response = client.post(f'/books/{book_id}/keywords', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'NoDataSent',
        'message': 'No data sent',
        'status': 400,
    }

    assert response_data == expected_data
    assert response.status_code == 400


def test_when_try_to_add_book_keyword_with_content_type_multipart_form_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 1
    data = {'keyword': 'palavra'}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, data=data)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'InvalidContentType',
        'message': 'Invalid Content-Type header',
        'status': 415,
    }

    assert response_data == expected_data
    assert response.status_code == 415


def test_when_try_to_add_book_keyword_without_auth_return_error_response(client: FlaskClient):
    book_id = 1
    data = {'keyword': 'palavra'}

    response = client.post(f'/books/{book_id}/keywords', json=data)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'MissingJWT',
        'message': 'JWT token not provided',
        'status': 401,
    }

    assert response_data == expected_data
    assert response.status_code == 401


def test_when_try_to_add_book_keyword_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    book_id = 1
    data = {'keyword': 'palavra'}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=data)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'InvalidJWT',
        'message': 'Invalid JWT token',
        'status': 401,
    }

    assert response_data == expected_data
    assert response.status_code == 401


def test_delete_book_keyword(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1
    book_keyword_id = 2

    response = client.delete(f'/books/{book_id}/keywords/{book_keyword_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {'error': False, 'status': 200}

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        book_keyword = db.session.get(BookKeyword, book_keyword_id)

        assert book_keyword is None


def test_when_try_to_delete_book_keyword_without_auth_return_error_response(client: FlaskClient):
    headers = {'Content-Type': 'application/json'}

    book_id = 1
    book_keyword_id = 2

    response = client.delete(f'/books/{book_id}/keywords/{book_keyword_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'MissingJWT',
        'message': 'JWT token not provided',
        'status': 401,
    }

    assert response_data == expected_data
    assert response.status_code == 401


def test_when_try_to_delete_book_keyword_with_invalid_auth_return_error_response(
    client: FlaskClient,
):
    headers = {
        'Authorization': f'Bearer 123',
        'Content-Type': 'application/json',
    }

    book_id = 1
    book_keyword_id = 2

    response = client.delete(f'/books/{book_id}/keywords/{book_keyword_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'InvalidJWT',
        'message': 'Invalid JWT token',
        'status': 401,
    }

    assert response_data == expected_data
    assert response.status_code == 401


def test_when_try_to_delete_last_book_keyword_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 2
    book_keyword_id = 3

    response = client.delete(f'/books/{book_id}/keywords/{book_keyword_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'BookMustHaveAtLeastOneKeyword',
        'message': f'The book {book_id} must have at least one keyword',
        'status': 400,
    }

    assert response_data == expected_data
    assert response.status_code == 400


def test_when_try_to_delete_book_keyword_does_not_exists_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1
    book_keyword_id = 100

    response = client.delete(f'/books/{book_id}/keywords/{book_keyword_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'BookKeywordDoesntExists',
        'message': f'The keyword {book_keyword_id} does not exist',
        'status': 404,
    }

    assert response_data == expected_data
    assert response.status_code == 404


def test_when_try_to_delete_book_keyword_from_book_does_not_exists_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 100
    book_keyword_id = 2

    response = client.delete(f'/books/{book_id}/keywords/{book_keyword_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'BookDoesntExists',
        'message': f'The book {book_id} does not exist',
        'status': 404,
    }

    assert response_data == expected_data
    assert response.status_code == 404


def test_when_try_to_delete_book_keyword_from_book_does_not_own_it_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 2
    book_keyword_id = 2

    response = client.delete(f'/books/{book_id}/keywords/{book_keyword_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'error': True,
        'error_name': 'BookDoesntOwnThisKeyword',
        'message': f'The keyword {book_keyword_id} does not belong to the book {book_id}',
        'status': 401,
    }

    assert response_data == expected_data
    assert response.status_code == 401
