import json

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from sqlalchemy import text

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
                "INSERT INTO users (username, password, img_url) VALUES ('test', 'Senha@123', 'url')"
            )
        )
        db.session.execute(
            text("INSERT INTO book_genres (genre) VALUES ('fábula'), ('ficção científica')")
        )
        db.session.execute(text("INSERT INTO book_kinds (kind) VALUES ('físico'), ('kindle')"))

        db.session.execute(
            text(
                """
                INSERT INTO books
                    (name, price, author, release_year, id_kind, id_genre)
                    VALUES
                        ('O Pequeno Príncipe', 10.99, 'Antoine de Saint-Exupéry', 1943, 1, 1),
                        ('Herdeiro do Império', 89.67, 'Timothy Zhan', 1993, 1, 1)
            """
            )
        )

        db.session.execute(
            text(
                """
                INSERT INTO book_imgs
                    (img_url, id_book)
                        VALUES
                            ('http://localhost:5000/books/photos/test.jpg', 1),
                            ('http://localhost:5000/books/photos/test2.jpg', 2)
                """
            )
        )

        db.session.execute(
            text(
                "INSERT INTO book_keywords (keyword, id_book) VALUES ('dramático', 1), ('infantil', 1), ('dramático', 2)"
            )
        )

        db.session.execute(text("INSERT INTO saved_books (id_user, id_book) VALUES (1, 1)"))

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


def test_return_all_saved_books(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.get('/books/saved', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': [
            {
                'id': 1,
                'name': 'O Pequeno Príncipe',
                'price': 10.99,
                'author': 'Antoine de Saint-Exupéry',
                'release_year': 1943,
                'book_kind': {'kind': 'físico', 'id': 1},
                'book_genre': {'genre': 'fábula', 'id': 1},
                'book_imgs': [{'id': 1, 'img_url': 'http://localhost:5000/books/photos/test.jpg'}],
                'book_keywords': [
                    {'id': 1, 'keyword': 'dramático'},
                    {'id': 2, 'keyword': 'infantil'},
                ],
            },
        ],
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_save_book(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.post('/books/2/save', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 201,
        'data': {
            'id': 2,
            'name': 'Herdeiro do Império',
            'price': 89.67,
            'author': 'Timothy Zhan',
            'release_year': 1993,
            'book_kind': {'kind': 'físico', 'id': 1},
            'book_genre': {'genre': 'fábula', 'id': 1},
            'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
            'book_keywords': [{'id': 3, 'keyword': 'dramático'}],
        },
    }

    assert response_data == expected_data
    assert response.status_code == 201

    with app.app_context():
        saved_book = db.session.get(SavedBook, 2)

        assert saved_book is not None
        assert saved_book.id == 2
        assert saved_book.book == db.session.get(Book, 2)
        user = db.session.get(User, 1)
        assert user is not None and saved_book.id_user == user.id


def test_when_try_to_save_book_with_id_from_book_already_saved_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.post('/books/1/save', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookAlreadySaved'
    assert response_data['status'] == 409
    assert response.status_code == 409


def test_when_try_to_save_book_with_id_from_book_doesnt_exists_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.post('/books/100/save', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_when_try_to_save_book_without_auth_return_error_response(client: FlaskClient):
    response = client.post('/books/2/save')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_save_book_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.post('/books/2/save', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_delete_saved_book(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.delete('/books/saved/1', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
    }

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        saved_book = db.session.get(SavedBook, 2)

        assert saved_book is None


def test_when_try_to_delete_saved_book_with_id_from_book_arent_saved_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.delete('/books/saved/2', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookArentSaved'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_when_try_to_delete_saved_book_with_id_from_book_doesnt_exists_return_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.delete('/books/saved/100', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_when_try_to_delete_saved_book_without_auth_return_error_response(client: FlaskClient):
    response = client.delete('/books/saved/1')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_delete_saved_book_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.delete('/books/saved/1', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401
