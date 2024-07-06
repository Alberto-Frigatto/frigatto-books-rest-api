import json
import os
import shutil
from datetime import datetime
from decimal import Decimal

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from app import create_app
from db import db
from model import Book, BookGenre, BookImg, BookKeyword, BookKind, User


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
                    'name': 'O Pequeno Príncipe',
                    'price': 10.99,
                    'author': 'Antoine de Saint Exupéry',
                    'release_year': 1943,
                    'id_kind': 1,
                    'id_genre': 1,
                },
                {
                    'name': 'Herdeiro do Império',
                    'price': 89.67,
                    'author': 'Timothy Zhan',
                    'release_year': 1993,
                    'id_kind': 1,
                    'id_genre': 1,
                },
                *[
                    {
                        'name': f'Livro {chr(97 + i)}',
                        'price': 20,
                        'author': 'Autor da Silva',
                        'release_year': 2000,
                        'id_kind': 1,
                        'id_genre': 1,
                    }
                    for i in range(2, 26)
                ],
            ],
        )

        db.session.execute(
            text("INSERT INTO book_imgs (img_url, id_book) VALUES (:img_url, :id_book)"),
            [
                {'img_url': 'http://localhost:5000/books/photos/test.jpg', 'id_book': 1},
                {'img_url': 'http://localhost:5000/books/photos/test2.jpg', 'id_book': 2},
                *[
                    {
                        'img_url': f'http://localhost:5000/books/photos/{chr(97 + i)}.jpg',
                        'id_book': i + 1,
                    }
                    for i in range(2, 26)
                ],
            ],
        )

        db.session.execute(
            text("INSERT INTO book_keywords (keyword, id_book) VALUES (:keyword, :id_book)"),
            [
                {'keyword': 'infantil', 'id_book': 1},
                {'keyword': 'dramático', 'id_book': 2},
                *[
                    {
                        'keyword': f'palavra {chr(97 + i)}',
                        'id_book': i + 1,
                    }
                    for i in range(2, 26)
                ],
            ],
        )
        db.session.commit()

    yield app

    clean_uploads()


def clean_uploads():
    dir = 'tests/uploads/'

    for file in os.listdir(dir):
        path = os.path.join(dir, file)

        if file != 'test.jpg':
            os.remove(path)

    if not os.path.exists('tests/uploads/test2.jpg'):
        shutil.copyfile('tests/resources/img-417kb.png', 'tests/uploads/test2.jpg')


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def access_token(app: Flask) -> str:
    with app.app_context():
        user = db.session.get(User, 1)
        return create_access_token(user)


def test_instantiate_Book():
    name = 'O Poderoso Chefão'
    price = Decimal('49.99')
    author = 'Mario Puzo'
    release_year = 1969

    book = Book(name, price, author, release_year)

    assert book.name == name
    assert book.price == price
    assert book.author == author
    assert book.release_year == release_year


def test_get_all_books_without_page(client: FlaskClient):
    response = client.get('/books')
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 1,
                'name': 'O Pequeno Príncipe',
                'price': 10.99,
                'author': 'Antoine de Saint Exupéry',
                'release_year': 1943,
                'book_kind': {'kind': 'físico', 'id': 1},
                'book_genre': {'genre': 'fábula', 'id': 1},
                'book_imgs': [{'id': 1, 'img_url': 'http://localhost:5000/books/photos/test.jpg'}],
                'book_keywords': [{'id': 1, 'keyword': 'infantil'}],
            },
            {
                'id': 2,
                'name': 'Herdeiro do Império',
                'price': 89.67,
                'author': 'Timothy Zhan',
                'release_year': 1993,
                'book_kind': {'kind': 'físico', 'id': 1},
                'book_genre': {'genre': 'fábula', 'id': 1},
                'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
                'book_keywords': [{'id': 2, 'keyword': 'dramático'}],
            },
            *[
                {
                    'id': i + 1,
                    'name': f'Livro {chr(97 + i)}',
                    'price': 20.0,
                    'author': 'Autor da Silva',
                    'release_year': 2000,
                    'book_kind': {'kind': 'físico', 'id': 1},
                    'book_genre': {'genre': 'fábula', 'id': 1},
                    'book_imgs': [
                        {
                            'id': i + 1,
                            'img_url': f'http://localhost:5000/books/photos/{chr(97 + i)}.jpg',
                        }
                    ],
                    'book_keywords': [
                        {
                            'keyword': f'palavra {chr(97 + i)}',
                            'id': i + 1,
                        }
                    ],
                }
                for i in range(2, 20)
            ],
        ],
        'has_next': True,
        'has_prev': False,
        'next_page': '/books?page=2',
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 26,
        'total_pages': 2,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_get_all_books_with_page_1(client: FlaskClient):
    response = client.get('/books?page=1')
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 1,
                'name': 'O Pequeno Príncipe',
                'price': 10.99,
                'author': 'Antoine de Saint Exupéry',
                'release_year': 1943,
                'book_kind': {'kind': 'físico', 'id': 1},
                'book_genre': {'genre': 'fábula', 'id': 1},
                'book_imgs': [{'id': 1, 'img_url': 'http://localhost:5000/books/photos/test.jpg'}],
                'book_keywords': [{'id': 1, 'keyword': 'infantil'}],
            },
            {
                'id': 2,
                'name': 'Herdeiro do Império',
                'price': 89.67,
                'author': 'Timothy Zhan',
                'release_year': 1993,
                'book_kind': {'kind': 'físico', 'id': 1},
                'book_genre': {'genre': 'fábula', 'id': 1},
                'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
                'book_keywords': [{'id': 2, 'keyword': 'dramático'}],
            },
            *[
                {
                    'id': i + 1,
                    'name': f'Livro {chr(97 + i)}',
                    'price': 20.0,
                    'author': 'Autor da Silva',
                    'release_year': 2000,
                    'book_kind': {'kind': 'físico', 'id': 1},
                    'book_genre': {'genre': 'fábula', 'id': 1},
                    'book_imgs': [
                        {
                            'id': i + 1,
                            'img_url': f'http://localhost:5000/books/photos/{chr(97 + i)}.jpg',
                        }
                    ],
                    'book_keywords': [
                        {
                            'keyword': f'palavra {chr(97 + i)}',
                            'id': i + 1,
                        }
                    ],
                }
                for i in range(2, 20)
            ],
        ],
        'has_next': True,
        'has_prev': False,
        'next_page': '/books?page=2',
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 26,
        'total_pages': 2,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_get_all_books_with_page_2(client: FlaskClient):
    response = client.get('/books?page=2')
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
                'book_imgs': [
                    {
                        'id': i + 1,
                        'img_url': f'http://localhost:5000/books/photos/{chr(97 + i)}.jpg',
                    }
                ],
                'book_keywords': [
                    {
                        'keyword': f'palavra {chr(97 + i)}',
                        'id': i + 1,
                    }
                ],
            }
            for i in range(20, 26)
        ],
        'has_next': False,
        'has_prev': True,
        'next_page': None,
        'page': 2,
        'per_page': 20,
        'prev_page':'/books?page=1',
        'total_items': 26,
        'total_pages': 2,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_get_all_books_with_page_3_return_error_response(client: FlaskClient):
    response = client.get('/books?page=3')
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


def test_get_book_by_id(client: FlaskClient):
    book_id = 2

    response = client.get(f'/books/{book_id}')
    response_data = json.loads(response.data)

    expected_data = {
        'id': book_id,
        'name': 'Herdeiro do Império',
        'price': 89.67,
        'author': 'Timothy Zhan',
        'release_year': 1993,
        'book_kind': {'kind': 'físico', 'id': 1},
        'book_genre': {'genre': 'fábula', 'id': 1},
        'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
        'book_keywords': [{'id': 2, 'keyword': 'dramático'}],
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_get_book_does_not_exists_return_error_response(client: FlaskClient):
    book_id = 100

    response = client.get(f'/books/{book_id}')
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookException',
        'code': 'BookDoesntExists',
        'message': f'The book {book_id} does not exist',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_create_book(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    new_book = {
        'name': 'O Poderoso Chefão',
        'price': 50,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': 1,
        'id_book_genre': 1,
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=new_book)
    response_data: dict = json.loads(response.data)

    new_book_id = 27
    expected_data = {
        'id': new_book_id,
        'name': new_book['name'],
        'price': float(new_book['price']),
        'author': new_book['author'],
        'release_year': new_book['release_year'],
        'book_genre': {'genre': 'fábula', 'id': 1},
        'book_kind': {'kind': 'físico', 'id': 1},
        'book_keywords': [
            {'id': 27, 'keyword': 'drama'},
            {'id': 28, 'keyword': 'máfia'},
            {'id': 29, 'keyword': 'itália'},
        ],
    }

    assert response_data['id'] == expected_data['id']
    assert response_data['name'] == expected_data['name']
    assert response_data['price'] == expected_data['price']
    assert response_data['author'] == expected_data['author']
    assert response_data['release_year'] == expected_data['release_year']
    assert response_data['book_genre'] == expected_data['book_genre']
    assert response_data['book_kind'] == expected_data['book_kind']
    assert isinstance(response_data['book_imgs'], list)
    assert len(response_data['book_imgs']) == 2
    assert all(isinstance(book_img, dict) for book_img in response_data['book_imgs'])
    assert all(isinstance(book_img['id'], int) for book_img in response_data['book_imgs'])
    assert all(isinstance(book_img['img_url'], str) for book_img in response_data['book_imgs'])
    assert all(
        book_img['img_url'].startswith('http://localhost:5000/books/photos/')
        for book_img in response_data['book_imgs']
    )
    assert all(book_img['img_url'].endswith('.jpg') for book_img in response_data['book_imgs'])
    assert response_data['book_keywords'] == expected_data['book_keywords']
    assert response.status_code == 201

    with app.app_context():
        book = db.session.get(Book, new_book_id)

        assert book is not None
        assert book.id == new_book_id
        assert book.name == expected_data['name']
        assert float(book.price) == expected_data['price']
        assert book.author == expected_data['author']
        assert book.release_year == expected_data['release_year']
        assert book.book_genre == db.session.get(BookGenre, expected_data['book_genre']['id'])
        assert book.book_kind == db.session.get(BookKind, expected_data['book_kind']['id'])
        assert book.book_imgs == [
            db.session.get(BookImg, book_img['id']) for book_img in response_data['book_imgs']
        ]
        assert book.book_keywords == [
            db.session.get(BookKeyword, book_keyword['id'])
            for book_keyword in response_data['book_keywords']
        ]

    dir = 'tests/uploads'
    for filename in os.listdir(dir):
        if filename not in ('test.jpg', 'test2.jpg'):
            assert os.path.isfile(os.path.join(dir, filename))


def test_when_try_to_create_book_without_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.post('/books', headers=headers)
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


def test_when_try_to_create_book_with_invalid_name_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    invalid_data = {
        'name': '',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [(open('tests/resources/img-417kb.png', 'rb'), 'image.png')],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['name'],
                'msg': 'String should have at least 2 characters',
                'type': 'string_too_short',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['name'] = 'Novo livro @#$123'
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['name'],
                'msg': "String should match pattern '^[a-zA-ZÀ-ÿç\\s\\d-]+$'",
                'type': 'string_pattern_mismatch',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['name'] = (
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    )
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['name'],
                'msg': 'String should have at most 80 characters',
                'type': 'string_too_long',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    del invalid_data['name']
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [{'loc': ['name'], 'msg': 'Field required', 'type': 'missing'}],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_book_with_invalid_price_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 'abc',
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [(open('tests/resources/img-417kb.png', 'rb'), 'image.png')],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['price'], 'msg': 'Input should be a valid decimal', 'type': 'decimal_parsing'}
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['price'] = 490000.99
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['price'],
                'msg': 'Decimal input should have no more than 6 digits in total',
                'type': 'decimal_max_digits',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['price'] = 49.9999
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['price'],
                'msg': 'Decimal input should have no more than 2 decimal places',
                'type': 'decimal_max_places',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['price'] = -1
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['price'], 'msg': 'Input should be greater than 0', 'type': 'greater_than'}
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    del invalid_data['price']
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [{'loc': ['price'], 'msg': 'Field required', 'type': 'missing'}],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_book_with_invalid_author_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo 123 $%¨',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [(open('tests/resources/img-417kb.png', 'rb'), 'image.png')],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['author'],
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

    invalid_data['author'] = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['author'],
                'msg': 'String should have at most 40 characters',
                'type': 'string_too_long',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['author'] = ''
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['author'],
                'msg': 'String should have at least 3 characters',
                'type': 'string_too_short',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    del invalid_data['author']
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [{'loc': ['author'], 'msg': 'Field required', 'type': 'missing'}],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_book_with_invalid_release_year_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': datetime.now().year + 1,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [(open('tests/resources/img-417kb.png', 'rb'), 'image.png')],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['release_year'],
                'msg': f'Input should be less than or equal to {datetime.now().year}',
                'type': 'less_than_equal',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['release_year'] = 123
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['release_year'],
                'msg': f'Input should be greater than or equal to 1000',
                'type': 'greater_than_equal',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['release_year'] = 'abcd'
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['release_year'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['release_year'] = ''
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['release_year'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['release_year'] = 1900.3
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['release_year'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    del invalid_data['release_year']
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [{'loc': ['release_year'], 'msg': 'Field required', 'type': 'missing'}],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_book_with_invalid_id_book_kind_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': 0,
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [(open('tests/resources/img-417kb.png', 'rb'), 'image.png')],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_kind'],
                'msg': 'Input should be greater than 0',
                'type': 'greater_than',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['id_book_kind'] = 'abc'
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_kind'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['id_book_kind'] = ''
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_kind'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['id_book_kind'] = 78.9
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_kind'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    del invalid_data['id_book_kind']
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [{'loc': ['id_book_kind'], 'msg': 'Field required', 'type': 'missing'}],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_book_with_invalid_id_book_genre_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': 0,
        'keywords': 'drama;máfia;itália',
        'imgs': [(open('tests/resources/img-417kb.png', 'rb'), 'image.png')],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_genre'],
                'msg': 'Input should be greater than 0',
                'type': 'greater_than',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['id_book_genre'] = 'abc'
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_genre'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['id_book_genre'] = 78.9
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_genre'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['id_book_genre'] = ''
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_genre'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    del invalid_data['id_book_genre']
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [{'loc': ['id_book_genre'], 'msg': 'Field required', 'type': 'missing'}],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_book_with_invalid_keywords_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': '',
        'imgs': [(open('tests/resources/img-417kb.png', 'rb'), 'image.png')],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['keywords'],
                'msg': 'Value error, Book must contains at least 1 keyword',
                'type': 'value_error',
            },
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['keywords'] = 'drama;máfia68;itáliaawdawdawdawdawdawdawd'
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['keywords', 2],
                'msg': 'String should have at most 20 characters',
                'type': 'string_too_long',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['keywords'] = 'drama;máfia#@;itália'
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['keywords', 1],
                'msg': "String should match pattern '^[a-zA-ZÀ-ÿç\\s\\d]+$'",
                'type': 'string_pattern_mismatch',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    del invalid_data['keywords']
    invalid_data['imgs'][0] = (open('tests/resources/img-417kb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [{'loc': ['keywords'], 'msg': 'Field required', 'type': 'missing'}],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_book_with_invalid_imgs_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-417kb.png', 'rb'), 'image.png'),
            (open('tests/resources/pdf-2mb.pdf', 'rb'), 'file.pdf'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['imgs', 1],
                'msg': 'Value error, The provided file is not an image',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['imgs'] = [
        (open('tests/resources/img-11.3mb.png', 'rb'), 'image.png'),
        (open('tests/resources/img-417kb.png', 'rb'), 'image.png'),
    ]

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['imgs', 0],
                'msg': 'Value error, The provided image is larger than 7MB',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['imgs'] = []

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['imgs'],
                'msg': 'Value error, Book must contains at least 1 image',
                'type': 'value_error',
            },
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['imgs'] = 'abc'

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['imgs'],
                'msg': 'Value error, The provided images are not files',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['imgs'] = [
        (open('tests/resources/text-2mb.txt', 'rb'), 'file.txt'),
    ]

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['imgs', 0],
                'msg': 'Value error, The provided file is not an image',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    invalid_data['imgs'] = [
        (open('tests/resources/img-417kb.png', 'rb'), f'image{i}.png') for i in range(6)
    ]

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['imgs'],
                'msg': 'Value error, Book must contains at most 5 images',
                'type': 'value_error',
            },
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    del invalid_data['imgs']

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['imgs'],
                'msg': 'Value error, Book must contains at least 1 image',
                'type': 'value_error',
            },
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_book_without_auth_returns_error_response(client: FlaskClient):
    response = client.post('/books')
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


def test_when_try_to_create_book_with_invalid_auth_returns_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.post('/books', headers=headers)
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


def test_when_try_to_create_book_already_exists_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    data = {
        'name': 'O Pequeno Príncipe',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [(open('tests/resources/img-417kb.png', 'rb'), 'image.png')],
    }

    response = client.post('/books', headers=headers, data=data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookException',
        'code': 'BookAlreadyExists',
        'message': f'The book "{data["name"]}" already exists',
        'status': 409,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409

    data['name'] = ' o pequeno príncipe '
    data['imgs'][0] = (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')

    response = client.post('/books', headers=headers, data=data)
    response_data = json.loads(response.data)

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409


def test_delete_book(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 2

    response = client.delete(f'/books/{book_id}', headers=headers)

    assert not response.data
    assert response.status_code == 204

    with app.app_context():
        book = db.session.get(Book, book_id)

        assert book is None

        assert not db.session.execute(
            text("SELECT COUNT(*) FROM book_imgs WHERE id_book = :id"), {'id': book_id}
        ).scalar()
        assert not db.session.execute(
            text("SELECT COUNT(*) FROM book_keywords WHERE id_book = :id"), {'id': book_id}
        ).scalar()


def test_when_try_to_delete_book_does_not_exists_return_error_message(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 100

    response = client.delete(f'/books/{book_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookException',
        'code': 'BookDoesntExists',
        'message': f'The book {book_id} does not exist',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_when_try_to_delete_book_without_auth_returns_error_response(client: FlaskClient):
    book_id = 2

    response = client.delete(f'/books/{book_id}')
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


def test_when_try_to_delete_book_with_invalid_auth_returns_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    book_id = 2

    response = client.delete(f'/books/{book_id}', headers=headers)
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


def test_update_name(client: FlaskClient, access_token: str, app: Flask):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'name': 'NOVO livro 123'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'id': book_id,
        'name': update['name'],
        'price': 89.67,
        'author': 'Timothy Zhan',
        'release_year': 1993,
        'book_kind': {'kind': 'físico', 'id': 1},
        'book_genre': {'genre': 'fábula', 'id': 1},
        'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
        'book_keywords': [{'id': 2, 'keyword': 'dramático'}],
    }

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        book = db.session.get(Book, book_id)

        assert book is not None
        assert book.id == book_id
        assert book.name == expected_data['name']
        assert float(book.price) == expected_data['price']
        assert book.author == expected_data['author']
        assert book.release_year == expected_data['release_year']
        assert book.book_genre == db.session.get(BookGenre, expected_data['book_genre']['id'])
        assert book.book_kind == db.session.get(BookKind, expected_data['book_kind']['id'])
        assert book.book_imgs == [db.session.get(BookImg, expected_data['book_imgs'][0]['id'])]
        assert book.book_keywords == [
            db.session.get(BookKeyword, expected_data['book_keywords'][0]['id'])
        ]


def test_update_name_with_the_same_name_but_in_UPPERCASE(
    client: FlaskClient, access_token: str, app: Flask
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'name': '   HERDEIRO DO IMPÉRIO'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'id': book_id,
        'name': update['name'].strip(),
        'price': 89.67,
        'author': 'Timothy Zhan',
        'release_year': 1993,
        'book_kind': {'kind': 'físico', 'id': 1},
        'book_genre': {'genre': 'fábula', 'id': 1},
        'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
        'book_keywords': [{'id': 2, 'keyword': 'dramático'}],
    }

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        book = db.session.get(Book, book_id)

        assert book is not None
        assert book.id == book_id
        assert book.name == expected_data['name']
        assert float(book.price) == expected_data['price']
        assert book.author == expected_data['author']
        assert book.release_year == expected_data['release_year']
        assert book.book_genre == db.session.get(BookGenre, expected_data['book_genre']['id'])
        assert book.book_kind == db.session.get(BookKind, expected_data['book_kind']['id'])
        assert book.book_imgs == [db.session.get(BookImg, expected_data['book_imgs'][0]['id'])]
        assert book.book_keywords == [
            db.session.get(BookKeyword, expected_data['book_keywords'][0]['id'])
        ]


def test_when_try_to_update_name_with_invalid_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'name': 'NOVO livro 123 -#$#&¨%'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['name'],
                'msg': "String should match pattern '^[a-zA-ZÀ-ÿç\\s\\d-]+$'",
                'type': 'string_pattern_mismatch',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'name': 'a'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['name'],
                'msg': 'String should have at least 2 characters',
                'type': 'string_too_short',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_update_name_with_name_from_existing_book_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'name': 'O Pequeno Príncipe'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookException',
        'code': 'BookAlreadyExists',
        'message': f'The book "{update["name"]}" already exists',
        'status': 409,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409

    update = {'name': '  o pequeno prínCIpe '}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 409


def test_update_price(client: FlaskClient, access_token: str, app: Flask):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'price': 1000}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'id': 2,
        'name': 'Herdeiro do Império',
        'price': update['price'],
        'author': 'Timothy Zhan',
        'release_year': 1993,
        'book_kind': {'kind': 'físico', 'id': 1},
        'book_genre': {'genre': 'fábula', 'id': 1},
        'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
        'book_keywords': [{'id': 2, 'keyword': 'dramático'}],
    }

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        book = db.session.get(Book, book_id)

        assert book is not None
        assert book.id == book_id
        assert book.name == expected_data['name']
        assert float(book.price) == expected_data['price']
        assert book.author == expected_data['author']
        assert book.release_year == expected_data['release_year']
        assert book.book_genre == db.session.get(BookGenre, expected_data['book_genre']['id'])
        assert book.book_kind == db.session.get(BookKind, expected_data['book_kind']['id'])
        assert book.book_imgs == [db.session.get(BookImg, expected_data['book_imgs'][0]['id'])]
        assert book.book_keywords == [
            db.session.get(BookKeyword, expected_data['book_keywords'][0]['id'])
        ]


def test_when_try_to_update_price_with_invalid_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'price': 100000.123}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['price'],
                'msg': 'Decimal input should have no more than 6 digits in total',
                'type': 'decimal_max_digits',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'price': 100000}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['price'],
                'msg': 'Decimal input should have no more than 4 digits before the decimal point',
                'type': 'decimal_whole_digits',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'price': 45.5646}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['price'],
                'msg': 'Decimal input should have no more than 2 decimal places',
                'type': 'decimal_max_places',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'price': -27}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['price'], 'msg': 'Input should be greater than 0', 'type': 'greater_than'}
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'price': ''}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['price'], 'msg': 'Input should be a valid decimal', 'type': 'decimal_parsing'}
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_update_author(client: FlaskClient, access_token: str, app: Flask):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'author': 'William Shakespeare'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'id': book_id,
        'name': 'Herdeiro do Império',
        'price': 89.67,
        'author': update['author'],
        'release_year': 1993,
        'book_kind': {'kind': 'físico', 'id': 1},
        'book_genre': {'genre': 'fábula', 'id': 1},
        'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
        'book_keywords': [{'id': 2, 'keyword': 'dramático'}],
    }

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        book = db.session.get(Book, book_id)

        assert book is not None
        assert book.id == book_id
        assert book.name == expected_data['name']
        assert float(book.price) == expected_data['price']
        assert book.author == expected_data['author']
        assert book.release_year == expected_data['release_year']
        assert book.book_genre == db.session.get(BookGenre, expected_data['book_genre']['id'])
        assert book.book_kind == db.session.get(BookKind, expected_data['book_kind']['id'])
        assert book.book_imgs == [db.session.get(BookImg, expected_data['book_imgs'][0]['id'])]
        assert book.book_keywords == [
            db.session.get(BookKeyword, expected_data['book_keywords'][0]['id'])
        ]


def test_when_try_to_update_author_with_invalid_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'author': 'autor 123'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['author'],
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

    update = {'author': 'autor ¨%$'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['author'],
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

    update = {'author': 'ab'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['author'],
                'msg': 'String should have at least 3 characters',
                'type': 'string_too_short',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_update_release_year(client: FlaskClient, access_token: str, app: Flask):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'release_year': 2014}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'id': book_id,
        'name': 'Herdeiro do Império',
        'price': 89.67,
        'author': 'Timothy Zhan',
        'release_year': update['release_year'],
        'book_kind': {'kind': 'físico', 'id': 1},
        'book_genre': {'genre': 'fábula', 'id': 1},
        'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
        'book_keywords': [{'id': 2, 'keyword': 'dramático'}],
    }

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        book = db.session.get(Book, book_id)

        assert book is not None
        assert book.id == book_id
        assert book.name == expected_data['name']
        assert float(book.price) == expected_data['price']
        assert book.author == expected_data['author']
        assert book.release_year == expected_data['release_year']
        assert book.book_genre == db.session.get(BookGenre, expected_data['book_genre']['id'])
        assert book.book_kind == db.session.get(BookKind, expected_data['book_kind']['id'])
        assert book.book_imgs == [db.session.get(BookImg, expected_data['book_imgs'][0]['id'])]
        assert book.book_keywords == [
            db.session.get(BookKeyword, expected_data['book_keywords'][0]['id'])
        ]


def test_when_try_to_update_release_year_with_invalid_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'release_year': 2000000}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['release_year'],
                'msg': f'Input should be less than or equal to {datetime.now().year}',
                'type': 'less_than_equal',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'release_year': 78.9}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['release_year'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'release_year': -27}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['release_year'],
                'msg': 'Input should be greater than or equal to 1000',
                'type': 'greater_than_equal',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'release_year': 'abc'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['release_year'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            },
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'release_year': ''}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['release_year'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            },
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_update_book_kind(client: FlaskClient, access_token: str, app: Flask):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'id_book_kind': 2}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'id': book_id,
        'name': 'Herdeiro do Império',
        'price': 89.67,
        'author': 'Timothy Zhan',
        'release_year': 1993,
        'book_kind': {'kind': 'kindle', 'id': 2},
        'book_genre': {'genre': 'fábula', 'id': 1},
        'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
        'book_keywords': [{'id': 2, 'keyword': 'dramático'}],
    }

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        book = db.session.get(Book, book_id)

        assert book is not None
        assert book.id == book_id
        assert book.name == expected_data['name']
        assert float(book.price) == expected_data['price']
        assert book.author == expected_data['author']
        assert book.release_year == expected_data['release_year']
        assert book.book_genre == db.session.get(BookGenre, expected_data['book_genre']['id'])
        assert book.book_kind == db.session.get(BookKind, expected_data['book_kind']['id'])
        assert book.book_imgs == [db.session.get(BookImg, expected_data['book_imgs'][0]['id'])]
        assert book.book_keywords == [
            db.session.get(BookKeyword, expected_data['book_keywords'][0]['id'])
        ]


def test_when_try_to_update_book_kind_with_invalid_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'id_book_kind': -1}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_kind'],
                'msg': 'Input should be greater than 0',
                'type': 'greater_than',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'id_book_kind': 78.23}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_kind'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'id_book_kind': 'abc'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_kind'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'id_book_kind': ''}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_kind'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_update_book_kind_with_id_from_book_kind_does_not_exists(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'id_book_kind': 100}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookKindException',
        'code': 'BookKindDoesntExists',
        'message': f'The book kind {update["id_book_kind"]} does not exist',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_update_book_genre(client: FlaskClient, access_token: str, app: Flask):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'id_book_genre': 2}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'id': book_id,
        'name': 'Herdeiro do Império',
        'price': 89.67,
        'author': 'Timothy Zhan',
        'release_year': 1993,
        'book_kind': {'kind': 'físico', 'id': 1},
        'book_genre': {'genre': 'ficção científica', 'id': 2},
        'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
        'book_keywords': [{'id': 2, 'keyword': 'dramático'}],
    }

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        book = db.session.get(Book, book_id)

        assert book is not None
        assert book.id == book_id
        assert book.name == expected_data['name']
        assert float(book.price) == expected_data['price']
        assert book.author == expected_data['author']
        assert book.release_year == expected_data['release_year']
        assert book.book_genre == db.session.get(BookGenre, expected_data['book_genre']['id'])
        assert book.book_kind == db.session.get(BookKind, expected_data['book_kind']['id'])
        assert book.book_imgs == [db.session.get(BookImg, expected_data['book_imgs'][0]['id'])]
        assert book.book_keywords == [
            db.session.get(BookKeyword, expected_data['book_keywords'][0]['id'])
        ]


def test_when_try_to_update_book_genre_with_invalid_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'id_book_genre': -1}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_genre'],
                'msg': 'Input should be greater than 0',
                'type': 'greater_than',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'id_book_genre': 78.23}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_genre'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'id_book_genre': 'abc'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_genre'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'id_book_genre': ''}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['id_book_genre'],
                'msg': 'Input should be a valid integer, unable to parse string as an integer',
                'type': 'int_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_update_book_genre_with_id_from_book_genre_does_not_exists(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'id_book_genre': 100}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookGenreException',
        'code': 'BookGenreDoesntExists',
        'message': f'The book genre {update["id_book_genre"]} does not exist',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_when_try_to_update_book_without_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2

    response = client.patch(f'/books/{book_id}', headers=headers)
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


def test_when_try_to_update_book_with_invalid_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    update = {'name': 'novo livro legal', 'prices': 789, 'year': 1234}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['prices'], 'msg': 'Extra inputs are not permitted', 'type': 'extra_forbidden'},
            {'loc': ['year'], 'msg': 'Extra inputs are not permitted', 'type': 'extra_forbidden'},
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_update_book_without_auth_returns_error_response(client: FlaskClient):
    headers = {'Content-Type': 'multipart/form-data'}

    book_id = 2
    update = {'name': 'NOVO livro'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
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


def test_when_try_to_update_book_with_invalid_auth_returns_error_response(client: FlaskClient):
    headers = {
        'Authorization': f'Bearer 123',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2

    update = {'name': 'NOVO livro'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
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
