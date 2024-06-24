import json

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from sqlalchemy import text

from app import create_app
from db import db
from model import BookGenre, User


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
        db.session.execute(text("INSERT INTO book_genres (genre) VALUES ('fantasia'), ('terror')"))
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


def test_instantiate_BookGenre():
    book_genre_name = 'novo gênero'
    book_genre = BookGenre(book_genre_name)

    assert book_genre.genre == book_genre_name


def test_return_all_book_genres(client: FlaskClient):
    response = client.get('/bookGenres')
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': [
            {'id': 1, 'genre': 'fantasia'},
            {'id': 2, 'genre': 'terror'},
        ],
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_return_book_genre_by_id(client: FlaskClient):
    book_genre_id = 1

    response = client.get(f'/bookGenres/{book_genre_id}')
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': {'id': 1, 'genre': 'fantasia'},
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_get_book_genre_does_not_exists_return_error_response(client: FlaskClient):
    book_genre_id = 100

    response = client.get(f'/bookGenres/{book_genre_id}')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookGenreDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_create_book_genre(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    new_book_genre = {'genre': 'genrele'}

    response = client.post('/bookGenres', headers=headers, json=new_book_genre)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 201,
        'data': {'id': 3, 'genre': 'genrele'},
    }

    assert response_data == expected_data
    assert response.status_code == 201

    with app.app_context():
        new_book_genre = db.session.get(BookGenre, 3)

        assert new_book_genre is not None
        assert new_book_genre.id == 3
        assert new_book_genre.genre == 'genrele'


def test_when_try_to_create_book_genre_with_content_type_multipart_form_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    new_book_genre = {'genre': 'genrele'}

    response = client.post('/bookGenres', headers=headers, data=new_book_genre)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidContentType'
    assert response_data['status'] == 415
    assert response.status_code == 415


def test_when_try_to_create_book_genre_already_exists_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    new_book_genre = {'genre': 'fantasia'}

    response = client.post('/bookGenres', headers=headers, json=new_book_genre)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookGenreAlreadyExists'
    assert response_data['status'] == 409
    assert response.status_code == 409


def test_when_try_to_create_book_genre_without_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.post('/bookGenres', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'NoDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_create_book_genre_with_invalid_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    invalid_data = {'genres': 'ebook'}

    response = client.post('/bookGenres', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = 456

    response = client.post('/bookGenres', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {'genre': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}

    response = client.post('/bookGenres', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {'genres': 'ebook234@'}

    response = client.post('/bookGenres', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_create_book_genre_without_auth_return_error_response(client: FlaskClient):
    response = client.post('/bookGenres')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_create_book_genre_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.post('/bookGenres', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_update_book_genre(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    updates = {'genre': 'batman'}

    book_genre_id = 2

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=updates)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': {'id': 2, 'genre': 'batman'},
    }

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        updated_book_genre = db.session.get(BookGenre, 2)

        assert updated_book_genre is not None
        assert updated_book_genre.id == 2
        assert updated_book_genre.genre == 'batman'


def test_when_try_to_update_book_genre_with_content_type_multipart_form_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    updates = {'genre': 'batman'}

    book_genre_id = 2

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, data=updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidContentType'
    assert response_data['status'] == 415
    assert response.status_code == 415


def test_when_try_to_update_book_genre_with_name_from_existing_book_genre_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_genre_id = 2

    updates = {'genre': ' FANtaSIa '}

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookGenreAlreadyExists'
    assert response_data['status'] == 409
    assert response.status_code == 409

    book_genre_id = 1

    updates = {'genre': ' TERROR'}

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=updates)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookGenreAlreadyExists'
    assert response_data['status'] == 409
    assert response.status_code == 409


def test_when_try_to_update_book_genre_without_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_genre_id = 2

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'NoDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_update_book_genre_with_invalid_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_genre_id = 2

    invalid_data = {'genres': 'ebook'}

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = 456

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {'genre': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {'genres': 'ebook234@'}

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_update_book_genre_without_auth_return_error_response(client: FlaskClient):
    response = client.patch('/bookGenres/1')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_update_book_genre_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.patch('/bookGenres/1', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_delete_book_genre(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_genre_id = 2

    response = client.delete(f'/bookGenres/{book_genre_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {'error': False, 'status': 200}

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        deleted_book_genre = db.session.get(BookGenre, 2)

        assert deleted_book_genre is None


def test_when_try_to_delete_book_genre_have_linked_book_return_error_response(
    client: FlaskClient, access_token: str, app: Flask
):
    with app.app_context():
        db.session.execute(text("INSERT INTO book_genres (genre) VALUES ('físico')"))
        db.session.execute(
            text(
                """
                INSERT INTO books
                            (name, price, author, release_year, id_kind, id_genre)
                            VALUES
                                ('O Pequeno Príncipe', 10.99, 'Antoine de Saint-Exupéry', 1943, 1, 2)
            """
            )
        )
        db.session.commit()

    headers = {'Authorization': f'Bearer {access_token}'}

    book_genre_id = 2

    response = client.delete(f'/bookGenres/{book_genre_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'ThereAreLinkedBooksWithThisBookGenre'
    assert response_data['status'] == 409
    assert response.status_code == 409


def test_when_try_to_delete_book_genre_does_not_exists_return_error_message(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_genre_id = 100

    response = client.delete(f'/bookGenres/{book_genre_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookGenreDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_when_try_to_delete_book_genre_without_auth_return_error_response(client: FlaskClient):
    response = client.delete('/bookGenres/1')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_delete_book_genre_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.delete('/bookGenres/1', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401
