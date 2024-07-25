import json
from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import text

from app import create_app
from db import db


@pytest.fixture()
def app():
    app = create_app(True)

    with app.app_context():
        db.create_all()
        db.session.execute(
            text("INSERT INTO book_genres (genre) VALUES (:genre)"),
            [
                {'genre': 'fantasia'},
                {'genre': 'ficção científica'},
                {'genre': 'suspense'},
                {'genre': 'técnico'},
                {'genre': 'terror'},
            ],
        )
        db.session.execute(
            text("INSERT INTO book_kinds (kind) VALUES (:kind)"),
            [{'kind': 'ebook'}, {'kind': 'físico'}, {'kind': 'kindle'}],
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
                    'name': 'O Poderoso Chefão',
                    'price': 50,
                    'author': 'Mario Puzo',
                    'release_year': 1962,
                    'id_kind': 1,
                    'id_genre': 3,
                },
                {
                    'name': 'O Pequeno Príncipe',
                    'price': 9.99,
                    'author': 'Antoine de Saint Exupéry',
                    'release_year': 1943,
                    'id_kind': 1,
                    'id_genre': 1,
                },
                {
                    'name': 'O Mundo Perdido',
                    'price': 115.47,
                    'author': 'Árthur Conan Doyle',
                    'release_year': 1912,
                    'id_kind': 3,
                    'id_genre': 5,
                },
                {
                    'name': '1984',
                    'price': 45.99,
                    'author': 'George Orwell',
                    'release_year': 1949,
                    'id_kind': 3,
                    'id_genre': 3,
                },
                {
                    'name': 'A Revolução dos Bichos',
                    'price': 5,
                    'author': 'George Orwell',
                    'release_year': 1945,
                    'id_kind': 2,
                    'id_genre': 3,
                },
            ],
        )
        db.session.execute(
            text("INSERT INTO book_keywords (keyword, id_book) VALUES (:keyword, :id_book)"),
            [
                {'keyword': 'máfia', 'id_book': 1},
                {'keyword': 'tiro', 'id_book': 1},
                {'keyword': 'família', 'id_book': 1},
                {'keyword': 'itália', 'id_book': 1},
                {'keyword': 'filosófico', 'id_book': 2},
                {'keyword': 'infantil', 'id_book': 2},
                {'keyword': 'clássico', 'id_book': 2},
                {'keyword': 'fantástico', 'id_book': 3},
                {'keyword': 'animais', 'id_book': 3},
                {'keyword': 'ditadura', 'id_book': 4},
                {'keyword': 'comunismo', 'id_book': 4},
                {'keyword': 'governo', 'id_book': 4},
                {'keyword': 'ditadura', 'id_book': 5},
                {'keyword': 'comunismo', 'id_book': 5},
                {'keyword': 'governo', 'id_book': 5},
                {'keyword': 'animais', 'id_book': 5},
            ],
        )

        db.session.commit()

    yield app


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


def test_search_books_by_name_using_query(client: FlaskClient):
    search = {'query': 'príncipe'}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 2,
                'name': 'O Pequeno Príncipe',
                'price': 9.99,
                'author': 'Antoine de Saint Exupéry',
                'release_year': 1943,
                'book_kind': {'kind': 'ebook', 'id': 1},
                'book_genre': {'genre': 'fantasia', 'id': 1},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 5, 'keyword': 'filosófico'},
                    {'id': 6, 'keyword': 'infantil'},
                    {'id': 7, 'keyword': 'clássico'},
                ],
            }
        ],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 1,
        'total_pages': 1,
    }

    assert response_data == expected_data
    assert response.status_code == 200

    search = {'query': ' biCHo '}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 5,
                'name': 'A Revolução dos Bichos',
                'price': 5.0,
                'author': 'George Orwell',
                'release_year': 1945,
                'book_kind': {'kind': 'físico', 'id': 2},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 13, 'keyword': 'ditadura'},
                    {'id': 14, 'keyword': 'comunismo'},
                    {'id': 15, 'keyword': 'governo'},
                    {'id': 16, 'keyword': 'animais'},
                ],
            }
        ],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 1,
        'total_pages': 1,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_search_books_by_author_using_query(client: FlaskClient):
    search = {'query': 'orwell'}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 4,
                'name': '1984',
                'price': 45.99,
                'author': 'George Orwell',
                'release_year': 1949,
                'book_kind': {'kind': 'kindle', 'id': 3},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 10, 'keyword': 'ditadura'},
                    {'id': 11, 'keyword': 'comunismo'},
                    {'id': 12, 'keyword': 'governo'},
                ],
            },
            {
                'id': 5,
                'name': 'A Revolução dos Bichos',
                'price': 5.0,
                'author': 'George Orwell',
                'release_year': 1945,
                'book_kind': {'kind': 'físico', 'id': 2},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 13, 'keyword': 'ditadura'},
                    {'id': 14, 'keyword': 'comunismo'},
                    {'id': 15, 'keyword': 'governo'},
                    {'id': 16, 'keyword': 'animais'},
                ],
            },
        ],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 2,
        'total_pages': 1,
    }

    assert response_data == expected_data
    assert response.status_code == 200

    search = {'query': 'mario'}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 1,
                'name': 'O Poderoso Chefão',
                'price': 50.0,
                'author': 'Mario Puzo',
                'release_year': 1962,
                'book_kind': {'kind': 'ebook', 'id': 1},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 1, 'keyword': 'máfia'},
                    {'id': 2, 'keyword': 'tiro'},
                    {'id': 3, 'keyword': 'família'},
                    {'id': 4, 'keyword': 'itália'},
                ],
            }
        ],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 1,
        'total_pages': 1,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_search_books_by_keyword_using_query(client: FlaskClient):
    search = {'query': 'comunismo'}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 4,
                'name': '1984',
                'price': 45.99,
                'author': 'George Orwell',
                'release_year': 1949,
                'book_kind': {'kind': 'kindle', 'id': 3},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 10, 'keyword': 'ditadura'},
                    {'id': 11, 'keyword': 'comunismo'},
                    {'id': 12, 'keyword': 'governo'},
                ],
            },
            {
                'id': 5,
                'name': 'A Revolução dos Bichos',
                'price': 5.0,
                'author': 'George Orwell',
                'release_year': 1945,
                'book_kind': {'kind': 'físico', 'id': 2},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 13, 'keyword': 'ditadura'},
                    {'id': 14, 'keyword': 'comunismo'},
                    {'id': 15, 'keyword': 'governo'},
                    {'id': 16, 'keyword': 'animais'},
                ],
            },
        ],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 2,
        'total_pages': 1,
    }

    assert response_data == expected_data
    assert response.status_code == 200

    search = {'query': 'animais'}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 3,
                'name': 'O Mundo Perdido',
                'price': 115.47,
                'release_year': 1912,
                'author': 'Árthur Conan Doyle',
                'book_kind': {'id': 3, 'kind': 'kindle'},
                'book_genre': {'genre': 'terror', 'id': 5},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 8, 'keyword': 'fantástico'},
                    {'id': 9, 'keyword': 'animais'},
                ],
            },
            {
                'id': 5,
                'name': 'A Revolução dos Bichos',
                'price': 5.0,
                'release_year': 1945,
                'author': 'George Orwell',
                'book_kind': {'id': 2, 'kind': 'físico'},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 13, 'keyword': 'ditadura'},
                    {'id': 14, 'keyword': 'comunismo'},
                    {'id': 15, 'keyword': 'governo'},
                    {'id': 16, 'keyword': 'animais'},
                ],
            },
        ],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 2,
        'total_pages': 1,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_search_books_with_query_doesnt_match_any_book_returns_empty_data(
    client: FlaskClient,
):
    search = {'query': 'aaa'}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 0,
        'total_pages': 0,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_search_books_with_invalid_query_returns_error_response(
    client: FlaskClient,
):
    search = {'query': 123}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['query'], 'msg': 'Input should be a valid string', 'type': 'string_type'}
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    search = {'query': [1, 2, 3]}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['query'], 'msg': 'Input should be a valid string', 'type': 'string_type'}
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_search_books_by_release_year_filter(client: FlaskClient):
    search = {'release_year': 1912}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 3,
                'name': 'O Mundo Perdido',
                'price': 115.47,
                'release_year': 1912,
                'author': 'Árthur Conan Doyle',
                'book_kind': {'id': 3, 'kind': 'kindle'},
                'book_genre': {'genre': 'terror', 'id': 5},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 8, 'keyword': 'fantástico'},
                    {'id': 9, 'keyword': 'animais'},
                ],
            },
        ],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 1,
        'total_pages': 1,
    }

    assert response_data == expected_data
    assert response.status_code == 200

    search = {'release_year': 1949}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 4,
                'name': '1984',
                'price': 45.99,
                'author': 'George Orwell',
                'release_year': 1949,
                'book_kind': {'kind': 'kindle', 'id': 3},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 10, 'keyword': 'ditadura'},
                    {'id': 11, 'keyword': 'comunismo'},
                    {'id': 12, 'keyword': 'governo'},
                ],
            },
        ],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 1,
        'total_pages': 1,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_search_books_with_release_year_filter_doesnt_match_any_book_returns_empty_data(
    client: FlaskClient,
):
    search = {'release_year': 2015}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 0,
        'total_pages': 0,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_search_books_with_invalid_release_year_filter_returns_error_response(
    client: FlaskClient,
):
    search = {'release_year': 'asd'}

    response = client.get('/search', json=search)
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

    search = {'release_year': [1, 2, 3]}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['release_year'], 'msg': 'Input should be a valid integer', 'type': 'int_type'}
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_search_books_by_kind_using_id_book_kind_filter(client: FlaskClient):
    search = {'id_book_kind': 1}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 1,
                'name': 'O Poderoso Chefão',
                'price': 50.0,
                'author': 'Mario Puzo',
                'release_year': 1962,
                'book_kind': {'kind': 'ebook', 'id': 1},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 1, 'keyword': 'máfia'},
                    {'id': 2, 'keyword': 'tiro'},
                    {'id': 3, 'keyword': 'família'},
                    {'id': 4, 'keyword': 'itália'},
                ],
            },
            {
                'id': 2,
                'name': 'O Pequeno Príncipe',
                'price': 9.99,
                'author': 'Antoine de Saint Exupéry',
                'release_year': 1943,
                'book_kind': {'kind': 'ebook', 'id': 1},
                'book_genre': {'genre': 'fantasia', 'id': 1},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 5, 'keyword': 'filosófico'},
                    {'id': 6, 'keyword': 'infantil'},
                    {'id': 7, 'keyword': 'clássico'},
                ],
            },
        ],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 2,
        'total_pages': 1,
    }

    assert response_data == expected_data
    assert response.status_code == 200

    search = {'id_book_kind': 3}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 3,
                'name': 'O Mundo Perdido',
                'price': 115.47,
                'release_year': 1912,
                'author': 'Árthur Conan Doyle',
                'book_kind': {'id': 3, 'kind': 'kindle'},
                'book_genre': {'genre': 'terror', 'id': 5},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 8, 'keyword': 'fantástico'},
                    {'id': 9, 'keyword': 'animais'},
                ],
            },
            {
                'id': 4,
                'name': '1984',
                'price': 45.99,
                'author': 'George Orwell',
                'release_year': 1949,
                'book_kind': {'kind': 'kindle', 'id': 3},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 10, 'keyword': 'ditadura'},
                    {'id': 11, 'keyword': 'comunismo'},
                    {'id': 12, 'keyword': 'governo'},
                ],
            },
        ],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 2,
        'total_pages': 1,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_search_books_with_invalid_id_book_kind_filter_returns_error_response(
    client: FlaskClient,
):
    search = {'id_book_kind': 'asd'}

    response = client.get('/search', json=search)
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

    search = {'id_book_kind': [1, 2, 3]}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['id_book_kind'], 'msg': 'Input should be a valid integer', 'type': 'int_type'}
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_search_books_with_id_book_kind_filter_doesnt_exists_returns_error_response(
    client: FlaskClient,
):
    search = {'id_book_kind': 100}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookKindException',
        'code': 'BookKindDoesntExist',
        'message': f'The book kind {search["id_book_kind"]} does not exist',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_search_books_by_genre_using_id_book_genre_filter(client: FlaskClient):
    search = {'id_book_genre': 3}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 1,
                'name': 'O Poderoso Chefão',
                'price': 50.0,
                'author': 'Mario Puzo',
                'release_year': 1962,
                'book_kind': {'kind': 'ebook', 'id': 1},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 1, 'keyword': 'máfia'},
                    {'id': 2, 'keyword': 'tiro'},
                    {'id': 3, 'keyword': 'família'},
                    {'id': 4, 'keyword': 'itália'},
                ],
            },
            {
                'id': 4,
                'name': '1984',
                'price': 45.99,
                'author': 'George Orwell',
                'release_year': 1949,
                'book_kind': {'kind': 'kindle', 'id': 3},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 10, 'keyword': 'ditadura'},
                    {'id': 11, 'keyword': 'comunismo'},
                    {'id': 12, 'keyword': 'governo'},
                ],
            },
            {
                'id': 5,
                'name': 'A Revolução dos Bichos',
                'price': 5.0,
                'release_year': 1945,
                'author': 'George Orwell',
                'book_kind': {'id': 2, 'kind': 'físico'},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 13, 'keyword': 'ditadura'},
                    {'id': 14, 'keyword': 'comunismo'},
                    {'id': 15, 'keyword': 'governo'},
                    {'id': 16, 'keyword': 'animais'},
                ],
            },
        ],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 3,
        'total_pages': 1,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_search_books_with_invalid_id_book_genre_filter_returns_error_response(
    client: FlaskClient,
):
    search = {'id_book_genre': 'asd'}

    response = client.get('/search', json=search)
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

    search = {'id_book_genre': [1, 2, 3]}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['id_book_genre'], 'msg': 'Input should be a valid integer', 'type': 'int_type'}
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_search_books_with_id_book_genre_filter_doesnt_exists_returns_error_response(
    client: FlaskClient,
):
    search = {'id_book_genre': 100}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookGenreException',
        'code': 'BookGenreDoesntExist',
        'message': f'The book genre {search["id_book_genre"]} does not exist',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_search_books_by_min_price_using_min_price_filter(client: FlaskClient):
    search = {'min_price': 50}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 1,
                'name': 'O Poderoso Chefão',
                'price': 50.0,
                'author': 'Mario Puzo',
                'release_year': 1962,
                'book_kind': {'kind': 'ebook', 'id': 1},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 1, 'keyword': 'máfia'},
                    {'id': 2, 'keyword': 'tiro'},
                    {'id': 3, 'keyword': 'família'},
                    {'id': 4, 'keyword': 'itália'},
                ],
            },
            {
                'id': 3,
                'name': 'O Mundo Perdido',
                'price': 115.47,
                'release_year': 1912,
                'author': 'Árthur Conan Doyle',
                'book_kind': {'id': 3, 'kind': 'kindle'},
                'book_genre': {'genre': 'terror', 'id': 5},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 8, 'keyword': 'fantástico'},
                    {'id': 9, 'keyword': 'animais'},
                ],
            },
        ],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 2,
        'total_pages': 1,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_search_books_with_invalid_min_price_filter_returns_error_response(
    client: FlaskClient,
):
    search = {'min_price': 'asd'}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['min_price'],
                'msg': 'Input should be a valid decimal',
                'type': 'decimal_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    search = {'min_price': [1, 2, 3]}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['min_price'],
                'msg': 'Decimal input should be an integer, float, string or Decimal object',
                'type': 'decimal_type',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_search_books_by_max_price_using_max_price_filter(client: FlaskClient):
    search = {'max_price': 46}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 2,
                'name': 'O Pequeno Príncipe',
                'price': 9.99,
                'author': 'Antoine de Saint Exupéry',
                'release_year': 1943,
                'book_kind': {'kind': 'ebook', 'id': 1},
                'book_genre': {'genre': 'fantasia', 'id': 1},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 5, 'keyword': 'filosófico'},
                    {'id': 6, 'keyword': 'infantil'},
                    {'id': 7, 'keyword': 'clássico'},
                ],
            },
            {
                'id': 4,
                'name': '1984',
                'price': 45.99,
                'author': 'George Orwell',
                'release_year': 1949,
                'book_kind': {'kind': 'kindle', 'id': 3},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 10, 'keyword': 'ditadura'},
                    {'id': 11, 'keyword': 'comunismo'},
                    {'id': 12, 'keyword': 'governo'},
                ],
            },
            {
                'id': 5,
                'name': 'A Revolução dos Bichos',
                'price': 5.0,
                'release_year': 1945,
                'author': 'George Orwell',
                'book_kind': {'id': 2, 'kind': 'físico'},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 13, 'keyword': 'ditadura'},
                    {'id': 14, 'keyword': 'comunismo'},
                    {'id': 15, 'keyword': 'governo'},
                    {'id': 16, 'keyword': 'animais'},
                ],
            },
        ],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 3,
        'total_pages': 1,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_search_books_with_invalid_max_price_filter_returns_error_response(
    client: FlaskClient,
):
    search = {'max_price': 'asd'}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['max_price'],
                'msg': 'Input should be a valid decimal',
                'type': 'decimal_parsing',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    search = {'max_price': [1, 2, 3]}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['max_price'],
                'msg': 'Decimal input should be an integer, float, string or Decimal object',
                'type': 'decimal_type',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_search_books_by_min_and_max_price_using_min_and_max_price_filter(client: FlaskClient):
    search = {'min_price': 40, 'max_price': 60}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'data': [
            {
                'id': 1,
                'name': 'O Poderoso Chefão',
                'price': 50.0,
                'author': 'Mario Puzo',
                'release_year': 1962,
                'book_kind': {'kind': 'ebook', 'id': 1},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 1, 'keyword': 'máfia'},
                    {'id': 2, 'keyword': 'tiro'},
                    {'id': 3, 'keyword': 'família'},
                    {'id': 4, 'keyword': 'itália'},
                ],
            },
            {
                'id': 4,
                'name': '1984',
                'price': 45.99,
                'author': 'George Orwell',
                'release_year': 1949,
                'book_kind': {'kind': 'kindle', 'id': 3},
                'book_genre': {'genre': 'suspense', 'id': 3},
                'book_imgs': [],
                'book_keywords': [
                    {'id': 10, 'keyword': 'ditadura'},
                    {'id': 11, 'keyword': 'comunismo'},
                    {'id': 12, 'keyword': 'governo'},
                ],
            },
        ],
        'has_next': False,
        'has_prev': False,
        'next_page': None,
        'page': 1,
        'per_page': 20,
        'prev_page': None,
        'total_items': 2,
        'total_pages': 1,
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_search_books_with_invalid_data_returns_error_response(
    client: FlaskClient,
):
    search = {'key': 'value'}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['key'], 'msg': 'Extra inputs are not permitted', 'type': 'extra_forbidden'}
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    search = 123

    response = client.get('/search', json=search)
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


def test_when_try_to_search_books_without_data_returns_error_response(
    client: FlaskClient,
):
    response = client.get('/search')
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


def test_when_try_to_search_books_with_content_type_multipart_form_data_returns_error_response(
    client: FlaskClient,
):
    headers = {
        'Content-Type': 'multipart/form-data',
    }

    search = {'query': 'chefão'}

    response = client.get('/search', headers=headers, data=search)
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
