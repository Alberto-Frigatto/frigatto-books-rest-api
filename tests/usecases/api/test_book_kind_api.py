import json
from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from app import create_app
from db import db
from model import BookKind, User


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
            text("INSERT INTO book_kinds (kind) VALUES (:kind)"),
            [{'kind': f'teste {chr(97 + i)}'} for i in range(26)],
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


def test_get_all_book_kinds_without_page(client: FlaskClient):
    response = client.get('/bookKinds')
    response_data = json.loads(response.data)

    expected_data = {
        'data': [{'kind': f'teste {chr(97 + i)}', 'id': i + 1} for i in range(20)],
        'has_next': True,
        'has_prev': False,
        'next_page': '/bookKinds?page=2',
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 26,
        'total_pages': 2,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_get_all_book_kinds_with_page_1(client: FlaskClient):
    response = client.get('/bookKinds?page=1')
    response_data = json.loads(response.data)

    expected_data = {
        'data': [{'kind': f'teste {chr(97 + i)}', 'id': i + 1} for i in range(20)],
        'has_next': True,
        'has_prev': False,
        'next_page': '/bookKinds?page=2',
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 26,
        'total_pages': 2,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_get_all_book_kinds_with_page_2(client: FlaskClient):
    response = client.get('/bookKinds?page=2')
    response_data = json.loads(response.data)

    expected_data = {
        'data': [{'kind': f'teste {chr(97 + i)}', 'id': i + 1} for i in range(20, 26)],
        'has_next': False,
        'has_prev': True,
        'next_page': None,
        'page': 2,
        'per_page': 20,
        'prev_page': '/bookKinds?page=1',
        'total_items': 26,
        'total_pages': 2,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_get_all_book_kinds_with_page_3_return_error_response(client: FlaskClient):
    response = client.get('/bookKinds?page=3')
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'PaginationPageDoesNotExists',
        'message': 'The page 3 does not exist',
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_get_book_kind_by_id(client: FlaskClient):
    book_kind_id = 1

    response = client.get(f'/bookKinds/{book_kind_id}')
    response_data = json.loads(response.data)

    expected_data = {'id': book_kind_id, 'kind': 'teste a'}

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_get_book_kind_does_not_exists_return_error_response(client: FlaskClient):
    book_kind_id = 100

    response = client.get(f'/bookKinds/{book_kind_id}')
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookKindException',
        'code': 'BookKindDoesntExists',
        'message': f'The book kind {book_kind_id} does not exist',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_create_book_kind(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    kind = 'kindle'
    new_book_kind = {'kind': kind}

    response = client.post('/bookKinds', headers=headers, json=new_book_kind)
    response_data = json.loads(response.data)

    new_book_kind_id = 27
    expected_data = {'id': new_book_kind_id, 'kind': kind}

    assert response_data == expected_data
    assert response.status_code == 201

    with app.app_context():
        new_book_kind = db.session.get(BookKind, new_book_kind_id)

        assert new_book_kind is not None
        assert new_book_kind.id == new_book_kind_id
        assert new_book_kind.kind == kind


def test_when_try_to_create_book_kind_with_content_type_multipart_form_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    new_book_kind = {'kind': 'batman'}

    response = client.post('/bookKinds', headers=headers, data=new_book_kind)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidContentType',
        'message': 'Invalid Content-Type header',
        'status': 415,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 415


def test_when_try_to_create_book_kind_already_exists_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    kind = ' TesTE W'
    new_book_kind = {'kind': kind}

    response = client.post('/bookKinds', headers=headers, json=new_book_kind)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookKindException',
        'code': 'BookKindAlreadyExists',
        'message': f'The book kind "{kind.lower().strip()}" already exists',
        'status': 409,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409


def test_when_try_to_create_book_kind_without_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.post('/bookKinds', headers=headers)
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


def test_when_try_to_create_book_kind_with_invalid_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    invalid_data = {'kinds': 'ebook'}

    response = client.post('/bookKinds', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['kind'], 'msg': 'Field required', 'type': 'missing'},
            {'loc': ['kinds'], 'msg': 'Extra inputs are not permitted', 'type': 'extra_forbidden'},
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = 456

    response = client.post('/bookKinds', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {'kind': 456}

    response = client.post('/bookKinds', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['kind'], 'msg': 'Input should be a valid string', 'type': 'string_type'}
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {'kind': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}

    response = client.post('/bookKinds', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['kind'],
                'msg': 'String should have at most 30 characters',
                'type': 'string_too_long',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {'kind': 'ebook234@'}

    response = client.post('/bookKinds', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['kind'],
                'msg': "String should match pattern '^[a-zA-ZÀ-ÿç\\s]+$'",
                'type': 'string_pattern_mismatch',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_book_kind_without_auth_return_error_response(client: FlaskClient):
    response = client.post('/bookKinds')
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


def test_when_try_to_create_book_kind_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.post('/bookKinds', headers=headers)
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


def test_update_book_kind(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    kind = 'batman'
    updates = {'kind': kind}

    book_kind_id = 2

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=updates)
    response_data = json.loads(response.data)

    expected_data = {'id': book_kind_id, 'kind': kind}

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        updated_book_kind = db.session.get(BookKind, book_kind_id)

        assert updated_book_kind is not None
        assert updated_book_kind.id == book_kind_id
        assert updated_book_kind.kind == kind


def test_update_book_genre_with_the_same_name_but_UPPERCASE(
    client: FlaskClient, access_token: str, app: Flask
):
    headers = {'Authorization': f'Bearer {access_token}'}

    kind = 'TESTE B'
    updates = {'kind': kind}

    book_kind_id = 2

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=updates)
    response_data = json.loads(response.data)

    expected_data = {'id': book_kind_id, 'kind': kind.lower()}

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        updated_book_kind = db.session.get(BookKind, book_kind_id)

        assert updated_book_kind is not None
        assert updated_book_kind.id == book_kind_id
        assert updated_book_kind.kind == kind.lower()


def test_when_try_to_update_book_kind_with_content_type_multipart_form_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    updates = {'kind': 'flash'}
    book_kind_id = 2

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, data=updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidContentType',
        'message': 'Invalid Content-Type header',
        'status': 415,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 415


def test_when_try_to_update_book_kind_without_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_kind_id = 2

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers)
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


def test_when_try_to_update_book_kind_with_name_from_existing_book_kind_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_kind_id = 2

    kind = ' TEste h   '
    updates = {'kind': kind}

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookKindException',
        'code': 'BookKindAlreadyExists',
        'message': f'The book kind "{kind.lower().strip()}" already exists',
        'status': 409,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409

    book_kind_id = 1

    kind = 'teste p'
    updates = {'kind': kind}

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookKindException',
        'code': 'BookKindAlreadyExists',
        'message': f'The book kind "{kind}" already exists',
        'status': 409,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409


def test_when_try_to_update_book_kind_with_invalid_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_kind_id = 2

    invalid_data = {'kinds': 'ebook'}

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['kind'], 'msg': 'Field required', 'type': 'missing'},
            {'loc': ['kinds'], 'msg': 'Extra inputs are not permitted', 'type': 'extra_forbidden'},
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = 456

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {'kind': 456}

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['kind'], 'msg': 'Input should be a valid string', 'type': 'string_type'}
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {'kind': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['kind'],
                'msg': 'String should have at most 30 characters',
                'type': 'string_too_long',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {'kind': 'ebook234@'}

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['kind'],
                'msg': "String should match pattern '^[a-zA-ZÀ-ÿç\\s]+$'",
                'type': 'string_pattern_mismatch',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_update_book_kind_without_auth_return_error_response(client: FlaskClient):
    response = client.patch('/bookKinds/1')
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


def test_when_try_to_update_book_kind_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.patch('/bookKinds/1', headers=headers)
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


def test_delete_book_kind(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_kind_id = 2

    response = client.delete(f'/bookKinds/{book_kind_id}', headers=headers)

    assert not response.data
    assert response.status_code == 204

    with app.app_context():
        deleted_book_kind = db.session.get(BookKind, book_kind_id)

        assert deleted_book_kind is None


def test_when_try_to_delete_book_kind_have_linked_book_return_error_response(
    client: FlaskClient, access_token: str, app: Flask
):
    with app.app_context():
        db.session.execute(text("INSERT INTO book_genres (genre) VALUES ('fantasia')"))
        db.session.execute(
            text(
                """--sql
                INSERT INTO books
                    (name, price, author, release_year, id_kind, id_genre)
                    VALUES (:name, :price, :author, :release_year, :id_kind, :id_genre)
                """
            ),
            {
                'name': 'O Pequeno Príncipe',
                'price': 10.99,
                'author': 'Antoine de Saint Exupéry',
                'release_year': 1943,
                'id_kind': 2,
                'id_genre': 1,
            },
        )
        db.session.commit()

    headers = {'Authorization': f'Bearer {access_token}'}
    book_kind_id = 2

    response = client.delete(f'/bookKinds/{book_kind_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookKindException',
        'code': 'ThereAreLinkedBooksWithThisBookKind',
        'message': f'The book genre {book_kind_id} cannot be deleted because there are books linked to this kind',
        'status': 409,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409


def test_when_try_to_delete_book_kind_does_not_exists_return_error_message(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_kind_id = 100

    response = client.delete(f'/bookKinds/{book_kind_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookKindException',
        'code': 'BookKindDoesntExists',
        'message': f'The book kind {book_kind_id} does not exist',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_when_try_to_delete_book_kind_without_auth_return_error_response(client: FlaskClient):
    response = client.delete('/bookKinds/1')
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


def test_when_try_to_delete_book_kind_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.delete('/bookKinds/1', headers=headers)
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
