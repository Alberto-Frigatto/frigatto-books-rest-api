import json

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from sqlalchemy import text

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
                "INSERT INTO users (username, password, img_url) VALUES ('test', 'Senha@123', 'url')"
            )
        )
        db.session.execute(text("INSERT INTO book_kinds (kind) VALUES ('físico'), ('ebook')"))
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


def test_instantiate_BookKind():
    book_kind_name = 'novo tipo'
    book_kind = BookKind(book_kind_name)

    assert book_kind.kind == book_kind_name


def test_return_all_book_kinds(client: FlaskClient):
    response = client.get('/bookKinds')
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': [
            {'id': 1, 'kind': 'físico'},
            {'id': 2, 'kind': 'ebook'},
        ],
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_return_book_kind_by_id(client: FlaskClient):
    book_kind_id = 1

    response = client.get(f'/bookKinds/{book_kind_id}')
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': {'id': 1, 'kind': 'físico'},
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_get_book_kind_does_not_exists_return_error_response(client: FlaskClient):
    book_kind_id = 100

    response = client.get(f'/bookKinds/{book_kind_id}')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookKindDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_create_book_kind(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    new_book_kind = {'kind': 'kindle'}

    response = client.post('/bookKinds', headers=headers, json=new_book_kind)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 201,
        'data': {'id': 3, 'kind': 'kindle'},
    }

    assert response_data == expected_data
    assert response.status_code == 201

    with app.app_context():
        new_book_kind = db.session.get(BookKind, 3)

        assert new_book_kind is not None
        assert new_book_kind.id == 3
        assert new_book_kind.kind == 'kindle'


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

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidContentType'
    assert response_data['status'] == 415
    assert response.status_code == 415


def test_when_try_to_create_book_kind_already_exists_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    new_book_kind = {'kind': 'ebook'}

    response = client.post('/bookKinds', headers=headers, json=new_book_kind)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookKindAlreadyExists'
    assert response_data['status'] == 409
    assert response.status_code == 409


def test_when_try_to_create_book_kind_without_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.post('/bookKinds', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'NoDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_create_book_kind_with_invalid_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    invalid_data = {'kinds': 'ebook'}

    response = client.post('/bookKinds', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = 456

    response = client.post('/bookKinds', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {'kind': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}

    response = client.post('/bookKinds', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {'kinds': 'ebook234@'}

    response = client.post('/bookKinds', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_create_book_kind_without_auth_return_error_response(client: FlaskClient):
    response = client.post('/bookKinds')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_create_book_kind_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.post('/bookKinds', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_update_book_kind(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    updates = {'kind': 'batman'}

    book_kind_id = 2

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=updates)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': {'id': 2, 'kind': 'batman'},
    }

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        updated_book_kind = db.session.get(BookKind, 2)

        assert updated_book_kind is not None
        assert updated_book_kind.id == 2
        assert updated_book_kind.kind == 'batman'


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

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidContentType'
    assert response_data['status'] == 415
    assert response.status_code == 415


def test_when_try_to_update_book_kind_without_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_kind_id = 2

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'NoDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_update_book_kind_with_name_from_existing_book_kind_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_kind_id = 2

    updates = {'kind': ' FÍsIcO'}

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookKindAlreadyExists'
    assert response_data['status'] == 409
    assert response.status_code == 409

    book_kind_id = 1

    updates = {'kind': 'EBOOK'}

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookKindAlreadyExists'
    assert response_data['status'] == 409
    assert response.status_code == 409


def test_when_try_to_update_book_kind_with_invalid_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_kind_id = 2

    invalid_data = {'kinds': 'ebook'}

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = 456

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {'kind': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {'kinds': 'ebook234@'}

    response = client.patch(f'/bookKinds/{book_kind_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_update_book_kind_without_auth_return_error_response(client: FlaskClient):
    response = client.patch('/bookKinds/1')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_update_book_kind_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.patch('/bookKinds/1', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_delete_book_kind(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_kind_id = 2

    response = client.delete(f'/bookKinds/{book_kind_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {'error': False, 'status': 200}

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        deleted_book_kind = db.session.get(BookKind, 3)

        assert deleted_book_kind is None


def test_when_try_to_delete_book_kind_have_linked_book_return_error_response(
    client: FlaskClient, access_token: str, app: Flask
):
    with app.app_context():
        db.session.execute(text("INSERT INTO book_genres (genre) VALUES ('fantasia')"))
        db.session.execute(
            text(
                """
                INSERT INTO books
                            (name, price, author, release_year, id_kind, id_genre)
                            VALUES
                                ('O Pequeno Príncipe', 10.99, 'Antoine de Saint-Exupéry', 1943, 2, 1)
            """
            )
        )
        db.session.commit()

    headers = {'Authorization': f'Bearer {access_token}'}

    book_kind_id = 2

    response = client.delete(f'/bookKinds/{book_kind_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'ThereAreLinkedBooksWithThisBookKind'
    assert response_data['status'] == 409
    assert response.status_code == 409


def test_when_try_to_delete_book_kind_does_not_exists_return_error_message(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_kind_id = 100

    response = client.delete(f'/bookKinds/{book_kind_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookKindDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_when_try_to_delete_book_kind_without_auth_return_error_response(client: FlaskClient):
    response = client.delete('/bookKinds/1')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_delete_book_kind_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.delete('/bookKinds/1', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401
