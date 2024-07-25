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
from model import Book, SavedBook, User


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
            text("INSERT INTO book_genres (genre) VALUES (:genre )"),
            [{'genre': 'fábula'}, {'genre': 'ficção científica'}],
        )
        db.session.execute(
            text("INSERT INTO book_kinds (kind) VALUES (:kind)"),
            [{'kind': 'físico'}, {'kind': 'kindle'}],
        )

        db.session.execute(
            text(
                """--sql
                INSERT INTO books
                    (name, price, author, release_year, id_kind, id_genre)
                    VALUES
                        (:name, :price, :author, :release_year, :id_kind, :id_genre)
                """
            ),
            [
                {
                    'name': f'Livro {chr(97 + i)}',
                    'price': 20,
                    'author': 'Autor da Silva',
                    'release_year': 2000,
                    'id_kind': 1,
                    'id_genre': 1,
                }
                for i in range(26)
            ],
        )

        db.session.execute(
            text("INSERT INTO saved_books (id_user, id_book) VALUES (:id_user, :id_book)"),
            [{'id_user': 1, 'id_book': i + 1} for i in range(25)],
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


def test_return_all_saved_books_without_page(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.get('/books/saved', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': i + 1,
                'name': f'Livro {chr(97 + i)}',
                'price': 20.0,
                'author': 'Autor da Silva',
                'release_year': 2000,
                'book_kind': {'kind': 'físico', 'id': 1},
                'book_genre': {'genre': 'fábula', 'id': 1},
                'book_imgs': [],
                'book_keywords': [],
            }
            for i in range(20)
        ],
        'has_next': True,
        'has_prev': False,
        'next_page': '/books/saved?page=2',
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 25,
        'total_pages': 2,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_return_all_saved_books_with_page_1(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.get('/books/saved?page=1', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': i + 1,
                'name': f'Livro {chr(97 + i)}',
                'price': 20.0,
                'author': 'Autor da Silva',
                'release_year': 2000,
                'book_kind': {'kind': 'físico', 'id': 1},
                'book_genre': {'genre': 'fábula', 'id': 1},
                'book_imgs': [],
                'book_keywords': [],
            }
            for i in range(20)
        ],
        'has_next': True,
        'has_prev': False,
        'next_page': '/books/saved?page=2',
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 25,
        'total_pages': 2,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_return_all_saved_books_with_page_2(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.get('/books/saved?page=2', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': i + 1,
                'name': f'Livro {chr(97 + i)}',
                'price': 20.0,
                'author': 'Autor da Silva',
                'release_year': 2000,
                'book_kind': {'kind': 'físico', 'id': 1},
                'book_genre': {'genre': 'fábula', 'id': 1},
                'book_imgs': [],
                'book_keywords': [],
            }
            for i in range(20, 25)
        ],
        'has_next': False,
        'has_prev': True,
        'next_page': None,
        'page': 2,
        'per_page': 20,
        'prev_page': '/books/saved?page=1',
        'total_items': 25,
        'total_pages': 2,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_get_all_saved_books_with_page_3_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('/books/saved?page=3', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'PaginationPageDoesntExist',
        'message': 'The page 3 does not exist',
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_save_book(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}
    book_id = 26

    response = client.post(f'/books/{book_id}/save', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'id': book_id,
        'name': f'Livro z',
        'price': 20.0,
        'author': 'Autor da Silva',
        'release_year': 2000,
        'book_kind': {'kind': 'físico', 'id': 1},
        'book_genre': {'genre': 'fábula', 'id': 1},
        'book_imgs': [],
        'book_keywords': [],
    }

    assert response_data == expected_data
    assert response.status_code == 201

    with app.app_context():
        saved_book = db.session.get(SavedBook, book_id)

        assert saved_book is not None
        assert saved_book.id == book_id
        assert saved_book.book == db.session.get(Book, book_id)
        user = db.session.get(User, 1)
        assert user is not None and saved_book.id_user == user.id


def test_when_try_to_save_book_with_id_from_book_already_saved_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}
    book_id = 1

    response = client.post(f'/books/{book_id}/save', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'SavedBookException',
        'code': 'BookAlreadySaved',
        'message': f'The book {book_id} is already saved by the user',
        'status': 409,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409


def test_when_try_to_save_book_with_id_from_book_doesnt_exists_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}
    book_id = 100

    response = client.post(f'/books/{book_id}/save', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookException',
        'code': 'BookDoesntExist',
        'message': f'The book {book_id} does not exist',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_when_try_to_save_book_without_auth_return_error_response(client: FlaskClient):
    response = client.post('/books/2/save')
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


def test_when_try_to_save_book_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.post('/books/2/save', headers=headers)
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


def test_delete_saved_book(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}
    book_id = 1

    response = client.delete(f'/books/saved/{book_id}', headers=headers)

    assert not response.data
    assert response.status_code == 204

    with app.app_context():
        saved_book = db.session.get(SavedBook, book_id)

        assert saved_book is None


def test_when_try_to_delete_saved_book_with_id_from_book_arent_saved_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}
    book_id = 26

    response = client.delete(f'/books/saved/{book_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'SavedBookException',
        'code': 'BookIsNotSaved',
        'message': f'The book {book_id} was not saved by the user',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_when_try_to_delete_saved_book_with_id_from_book_doesnt_exists_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}
    book_id = 100

    response = client.delete(f'/books/saved/{book_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookException',
        'code': 'BookDoesntExist',
        'message': f'The book {book_id} does not exist',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_when_try_to_delete_saved_book_without_auth_return_error_response(client: FlaskClient):
    response = client.delete('/books/saved/1')
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


def test_when_try_to_delete_saved_book_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.delete('/books/saved/1', headers=headers)
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
