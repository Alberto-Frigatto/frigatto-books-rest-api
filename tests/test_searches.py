import json
from pprint import pprint

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
            text(
                """
            INSERT INTO book_genres
                (genre)
                VALUES ('fantasia'),
                        ('ficção científica'),
                        ('suspense'),
                        ('técnico'),
                        ('terror')
        """
            )
        )
        db.session.execute(
            text(
                """
            INSERT INTO book_kinds
                (kind)
                VALUES ('ebook'),
                        ('físico'),
                        ('kindle')
        """
            )
        )
        db.session.execute(
            text(
                """
            INSERT INTO books
                (name, price, author, release_year, id_kind, id_genre)
                VALUES ('O Poderoso Chefão', 50.00, 'Mario Puzo', 1962, 1, 3),
                        ('O Pequeno Príncipe', 9.99, 'Antoine de Saint Exupéry', 1943, 1, 1),
                        ('O Mundo Perdido', 115.47, 'Árthur Conan Doyle', 1912, 3, 5),
                        ('1984', 45.99, 'George Orwell', 1949, 3, 3),
                        ('A Revolução dos Bichos', 5.00, 'George Orwell', 1945, 2, 3)
        """
            )
        )
        db.session.execute(
            text(
                """
            INSERT INTO book_keywords
                (keyword, id_book)
                VALUES ('máfia', 1),
                        ('tiro', 1),
                        ('família', 1),
                        ('itália', 1),
                        ('filosófico', 2),
                        ('infantil', 2),
                        ('clássico', 2),
                        ('fantástico', 3),
                        ('animais', 3),
                        ('ditadura', 4),
                        ('comunismo', 4),
                        ('governo', 4),
                        ('ditadura', 5),
                        ('comunismo', 5),
                        ('governo', 5),
                        ('animais', 5);
        """
            )
        )

        db.session.commit()

    yield app


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


def test_search_books_by_name_using_query(client: FlaskClient):
    search = {
        'query': 'príncipe',
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
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
    }

    assert response_data == expected_data
    assert response.status_code == 200

    search = {
        'query': ' biCHo ',
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
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
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_search_books_by_author_using_query(client: FlaskClient):
    search = {
        'query': 'orwell',
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
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
    }

    assert response_data == expected_data
    assert response.status_code == 200

    search = {
        'query': 'mario',
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
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
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_search_books_by_keyword_using_query(client: FlaskClient):
    search = {
        'query': 'comunismo',
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
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
    }

    assert response_data == expected_data
    assert response.status_code == 200

    search = {
        'query': 'animais',
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
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
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_search_books_with_query_doesnt_match_any_book_returns_empty_data(
    client: FlaskClient,
):
    search = {
        'query': 'aaa',
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': [],
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_search_books_with_invalid_query_returns_error_response(
    client: FlaskClient,
):
    search = {
        'query': 123,
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400

    search = {
        'query': [1, 2, 3],
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400


def test_search_books_by_release_year_filter(client: FlaskClient):
    search = {
        'filter': {
            'release_year': 1912,
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
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
    }

    assert response_data == expected_data
    assert response.status_code == 200

    search = {
        'filter': {
            'release_year': 1949,
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
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
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_search_books_with_release_year_filter_doesnt_match_any_book_returns_empty_data(
    client: FlaskClient,
):
    search = {
        'filter': {
            'release_year': 2015,
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': [],
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_search_books_with_invalid_release_year_filter_returns_error_response(
    client: FlaskClient,
):
    search = {
        'filter': {
            'release_year': 'asd',
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400

    search = {
        'filter': {
            'release_year': [1, 2, 3],
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400


def test_search_books_by_kind_using_id_kind_filter(client: FlaskClient):
    search = {
        'filter': {
            'id_kind': 1,
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
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
    }

    assert response_data == expected_data
    assert response.status_code == 200

    search = {
        'filter': {
            'id_kind': 3,
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
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
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_search_books_with_invalid_id_kind_filter_returns_error_response(
    client: FlaskClient,
):
    search = {
        'filter': {
            'id_kind': 'asd',
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400

    search = {
        'filter': {
            'id_kind': [1, 2, 3],
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400


def test_when_try_to_search_books_with_id_kind_filter_doesnt_exists_returns_error_response(
    client: FlaskClient,
):
    search = {
        'filter': {
            'id_kind': 100,
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 404
    assert response_data['error_name'] == 'BookKindDoesntExists'
    assert response.status_code == 404


def test_search_books_by_genre_using_id_genre_filter(client: FlaskClient):
    search = {
        'filter': {
            'id_genre': 3,
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
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
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_search_books_with_invalid_id_genre_filter_returns_error_response(
    client: FlaskClient,
):
    search = {
        'filter': {
            'id_genre': 'asd',
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400

    search = {
        'filter': {
            'id_genre': [1, 2, 3],
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400


def test_when_try_to_search_books_with_id_genre_filter_doesnt_exists_returns_error_response(
    client: FlaskClient,
):
    search = {
        'filter': {
            'id_genre': 100,
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 404
    assert response_data['error_name'] == 'BookGenreDoesntExists'
    assert response.status_code == 404


def test_search_books_by_min_price_using_min_price_filter(client: FlaskClient):
    search = {
        'filter': {
            'price': {
                'min': 50,
            }
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
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
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_search_books_with_invalid_min_price_filter_returns_error_response(
    client: FlaskClient,
):
    search = {'filter': {'price': {'min': 'asd'}}}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400

    search = {
        'filter': {
            'price': {
                'min': [1, 2, 3],
            }
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400


def test_search_books_by_max_price_using_max_price_filter(client: FlaskClient):
    search = {
        'filter': {
            'price': {
                'max': 46,
            }
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
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
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_search_books_with_invalid_max_price_filter_returns_error_response(
    client: FlaskClient,
):
    search = {'filter': {'price': {'max': 'asd'}}}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400

    search = {
        'filter': {
            'price': {
                'max': [1, 2, 3],
            }
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400


def test_search_books_by_min_and_max_price_using_min_and_max_price_filter(client: FlaskClient):
    search = {
        'filter': {
            'price': {
                'min': 40,
                'max': 60,
            }
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
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
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_search_books_with_invalid_price_filter_returns_error_response(
    client: FlaskClient,
):
    search = {
        'filter': {
            'price': 'asd',
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400

    search = {
        'filter': {
            'price': [1, 2, 3],
        }
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400


def test_when_try_to_search_books_with_invalid_filter_returns_error_response(
    client: FlaskClient,
):
    search = {
        'filter': 'asd',
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400

    search = {
        'filter': [1, 2, 3],
    }

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400


def test_when_try_to_search_books_with_invalid_data_returns_error_response(
    client: FlaskClient,
):
    search = {'key': 'value'}

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400

    search = 123

    response = client.get('/search', json=search)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response.status_code == 400


def test_when_try_to_search_books_without_data_returns_error_response(
    client: FlaskClient,
):
    response = client.get('/search')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['status'] == 400
    assert response_data['error_name'] == 'NoDataSent'
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

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidContentType'
    assert response_data['status'] == 415
    assert response.status_code == 415
