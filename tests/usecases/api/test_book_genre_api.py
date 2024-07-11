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
from model import BookGenre, User


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
            text("INSERT INTO book_genres (genre) VALUES (:genre)"),
            [{'genre': f'teste {chr(97 + i)}'} for i in range(26)],
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


def test_instantiate_BookGenre():
    book_genre_name = 'novo gênero'
    book_genre = BookGenre(book_genre_name)

    assert book_genre.genre == book_genre_name


def test_get_all_book_genres_without_page(client: FlaskClient):
    response = client.get('/bookGenres')
    response_data = json.loads(response.data)

    expected_data = {
        'data': [{'genre': f'teste {chr(97 + i)}', 'id': i + 1} for i in range(20)],
        'has_next': True,
        'has_prev': False,
        'next_page': '/bookGenres?page=2',
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 26,
        'total_pages': 2,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_get_all_book_genres_with_page_1(client: FlaskClient):
    response = client.get('/bookGenres?page=1')
    response_data = json.loads(response.data)

    expected_data = {
        'data': [{'genre': f'teste {chr(97 + i)}', 'id': i + 1} for i in range(20)],
        'has_next': True,
        'has_prev': False,
        'next_page': '/bookGenres?page=2',
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 26,
        'total_pages': 2,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_get_all_book_genres_with_page_2(client: FlaskClient):
    response = client.get('/bookGenres?page=2')
    response_data = json.loads(response.data)

    expected_data = {
        'data': [{'genre': f'teste {chr(97 + i)}', 'id': i + 1} for i in range(20, 26)],
        'has_next': False,
        'has_prev': True,
        'next_page': None,
        'page': 2,
        'per_page': 20,
        'prev_page': '/bookGenres?page=1',
        'total_items': 26,
        'total_pages': 2,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_get_all_book_genres_with_page_3_return_error_response(client: FlaskClient):
    response = client.get('/bookGenres?page=3')
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


def test_get_book_genre_by_id(client: FlaskClient):
    book_genre_id = 1

    response = client.get(f'/bookGenres/{book_genre_id}')
    response_data = json.loads(response.data)

    expected_data = {'id': book_genre_id, 'genre': 'teste a'}

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_get_book_genre_does_not_exists_return_error_response(client: FlaskClient):
    book_genre_id = 100

    response = client.get(f'/bookGenres/{book_genre_id}')
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookGenreException',
        'code': 'BookGenreDoesntExists',
        'message': f'The book genre {book_genre_id} does not exist',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_create_book_genre(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    genre = 'novo gênero'
    new_book_genre = {'genre': genre}

    response = client.post('/bookGenres', headers=headers, json=new_book_genre)
    response_data = json.loads(response.data)

    id_new_book_genre = 27
    expected_data = {'id': id_new_book_genre, 'genre': genre}

    assert response_data == expected_data
    assert response.status_code == 201

    with app.app_context():
        new_book_genre = db.session.get(BookGenre, id_new_book_genre)

        assert new_book_genre is not None
        assert new_book_genre.id == id_new_book_genre
        assert new_book_genre.genre == genre


def test_when_try_to_create_book_genre_with_content_type_multipart_form_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    new_book_genre = {'genre': 'novo gênero'}

    response = client.post('/bookGenres', headers=headers, data=new_book_genre)
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


def test_when_try_to_create_book_genre_already_exists_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    new_book_genre = {'genre': 'teste a'}

    response = client.post('/bookGenres', headers=headers, json=new_book_genre)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookGenreException',
        'code': 'BookGenreAlreadyExists',
        'message': 'The book genre "teste a" already exists',
        'status': 409,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409


def test_when_try_to_create_book_genre_without_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.post('/bookGenres', headers=headers)
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


def test_when_try_to_create_book_genre_with_invalid_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    invalid_data = {'genres': 'ebook'}

    response = client.post('/bookGenres', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['genre'], 'msg': 'Field required', 'type': 'missing'},
            {'loc': ['genres'], 'msg': 'Extra inputs are not permitted', 'type': 'extra_forbidden'},
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = 456

    response = client.post('/bookGenres', headers=headers, json=invalid_data)
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

    invalid_data = {'genre': 456}

    response = client.post('/bookGenres', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['genre'], 'msg': 'Input should be a valid string', 'type': 'string_type'},
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {'genre': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}

    response = client.post('/bookGenres', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['genre'],
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

    invalid_data = {'genres': 'ebook234@'}

    response = client.post('/bookGenres', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['genre'], 'msg': 'Field required', 'type': 'missing'},
            {'loc': ['genres'], 'msg': 'Extra inputs are not permitted', 'type': 'extra_forbidden'},
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_book_genre_without_auth_return_error_response(client: FlaskClient):
    response = client.post('/bookGenres')
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


def test_when_try_to_create_book_genre_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.post('/bookGenres', headers=headers)
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


def test_update_book_genre(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    genre = 'batman'
    updates = {'genre': genre}

    book_genre_id = 2

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=updates)
    response_data = json.loads(response.data)

    expected_data = {'id': book_genre_id, 'genre': genre}

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        updated_book_genre = db.session.get(BookGenre, book_genre_id)

        assert updated_book_genre is not None
        assert updated_book_genre.id == book_genre_id
        assert updated_book_genre.genre == genre


def test_update_book_genre_with_the_same_name_but_UPPERCASE(
    client: FlaskClient, access_token: str, app: Flask
):
    headers = {'Authorization': f'Bearer {access_token}'}

    genre = 'TESTE B'
    updates = {'genre': genre}

    book_genre_id = 2

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=updates)
    response_data = json.loads(response.data)

    expected_data = {'id': book_genre_id, 'genre': genre.lower()}

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        updated_book_genre = db.session.get(BookGenre, book_genre_id)

        assert updated_book_genre is not None
        assert updated_book_genre.id == book_genre_id
        assert updated_book_genre.genre == genre.lower()


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


def test_when_try_to_update_book_genre_with_name_from_existing_book_genre_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_genre_id = 2

    updates = {'genre': ' TesTE Z '}

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookGenreException',
        'code': 'BookGenreAlreadyExists',
        'message': 'The book genre "teste z" already exists',
        'status': 409,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409

    book_genre_id = 1

    updates = {'genre': ' TESTE b'}

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=updates)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookGenreException',
        'code': 'BookGenreAlreadyExists',
        'message': 'The book genre "teste b" already exists',
        'status': 409,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409


def test_when_try_to_update_book_genre_without_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_genre_id = 2

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers)
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


def test_when_try_to_update_book_genre_with_invalid_data_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_genre_id = 2

    invalid_data = {'genres': 'ebook'}

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['genre'], 'msg': 'Field required', 'type': 'missing'},
            {'loc': ['genres'], 'msg': 'Extra inputs are not permitted', 'type': 'extra_forbidden'},
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = 456

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=invalid_data)
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

    invalid_data = {'genre': 456}

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['genre'], 'msg': 'Input should be a valid string', 'type': 'string_type'}
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data = {'genre': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['genre'],
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

    invalid_data = {'genres': 'ebook234@'}

    response = client.patch(f'/bookGenres/{book_genre_id}', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['genre'], 'msg': 'Field required', 'type': 'missing'},
            {'loc': ['genres'], 'msg': 'Extra inputs are not permitted', 'type': 'extra_forbidden'},
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_update_book_genre_without_auth_return_error_response(client: FlaskClient):
    response = client.patch('/bookGenres/1')
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


def test_when_try_to_update_book_genre_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.patch('/bookGenres/1', headers=headers)
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


def test_delete_book_genre(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_genre_id = 2

    response = client.delete(f'/bookGenres/{book_genre_id}', headers=headers)

    assert not response.data
    assert response.status_code == 204

    with app.app_context():
        deleted_book_genre = db.session.get(BookGenre, book_genre_id)

        assert deleted_book_genre is None


def test_when_try_to_delete_book_genre_have_linked_book_return_error_response(
    client: FlaskClient, access_token: str, app: Flask
):
    with app.app_context():
        db.session.execute(
            text("INSERT INTO book_genres (genre) VALUES (:genre)"), {'genre': 'físico'}
        )
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
                'id_kind': 1,
                'id_genre': 2,
            },
        )
        db.session.commit()

    headers = {'Authorization': f'Bearer {access_token}'}

    book_genre_id = 2

    response = client.delete(f'/bookGenres/{book_genre_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookGenreException',
        'code': 'ThereAreLinkedBooksWithThisBookGenre',
        'message': f'The book genre {book_genre_id} cannot be deleted because there are books linked to this genre',
        'status': 409,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409


def test_when_try_to_delete_book_genre_does_not_exists_return_error_message(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_genre_id = 100

    response = client.delete(f'/bookGenres/{book_genre_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookGenreException',
        'code': 'BookGenreDoesntExists',
        'message': f'The book genre {book_genre_id} does not exist',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_when_try_to_delete_book_genre_without_auth_return_error_response(client: FlaskClient):
    response = client.delete('/bookGenres/1')
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


def test_when_try_to_delete_book_genre_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.delete('/bookGenres/1', headers=headers)
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
