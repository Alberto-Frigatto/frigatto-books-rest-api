import datetime
import json
import os
import shutil

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from app import create_app
from db import db
from handle_errors import CustomError
from models import Book, User
from schemas import books_schema


@pytest.fixture()
def app():
    app = create_app(True)

    with app.app_context():
        db.create_all()

        db.session.execute(
            text(
                f"""
                INSERT INTO users (username, password, img_url)
                    VALUES ('test', '{generate_password_hash('Senha@123')}', 'http://localhost:5000/users/photos/test.jpg')
                """
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

        db.session.commit()

    yield app

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
    price = '49.99'
    author = 'Mario Puzo'
    release_year = '1969'

    book = Book(name, price, author, release_year)

    assert book.name == name
    assert book.price == float(price)
    assert book.author == author
    assert book.release_year == int(release_year)


def test_when_Book_receives_invalid_name_raises_CustomError():
    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('', '49.99', 'Mario Puzo', '1969')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('123', '49.99', 'Mario Puzo', '1969')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('#@#$@#$!#@!@', '49.99', 'Mario Puzo', '1969')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book(
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            '49.99',
            'Mario Puzo',
            '1969',
        )

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book(None, '49.99', 'Mario Puzo', '1969')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book(123, '49.99', 'Mario Puzo', '1969')


def test_when_Book_receives_invalid_price_raises_CustomError():
    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '', 'Mario Puzo', '1969')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', None, 'Mario Puzo', '1969')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '49.999', 'Mario Puzo', '1969')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '4444444444449.99', 'Mario Puzo', '1969')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', 'abc', 'Mario Puzo', '1969')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '-1', 'Mario Puzo', '1969')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '49,99', 'Mario Puzo', '1969')


def test_when_Book_receives_invalid_author_raises_CustomError():
    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '49.99', '', '1969')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '49.99', '123', '1969')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '49.99', '#@#$@#$!#@!@', '1969')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book(
            'O Poderoso Chefão',
            '49.99',
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            '1969',
        )

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '49.99', None, '1969')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '49.99', 123, '1969')


def test_when_Book_receives_invalid_release_year_raises_CustomError():
    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '49.99', 'Mario Puzo', '')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '49.99', 'Mario Puzo', None)

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '49.99', 'Mario Puzo', '1899')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '49.99', 'Mario Puzo', datetime.datetime.now().year + 1)

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '49.99', 'Mario Puzo', '1969.45')

    with pytest.raises(CustomError, match=r'^InvalidDataSent$'):
        Book('O Poderoso Chefão', '49.99', 'Mario Puzo', 123)


def test_create_book(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    new_book = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
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
    response_data = json.loads(response.data)

    assert not response_data['error']
    assert response_data['status'] == 201
    assert response_data['data']
    assert response_data['data']['name'] == 'O Poderoso Chefão'
    assert response_data['data']['price'] == 49.99
    assert response_data['data']['author'] == 'Mario Puzo'
    assert response_data['data']['release_year'] == 1969
    assert response_data['data']['book_genre'] == {'genre': 'fábula', 'id': 1}
    assert len(response_data['data']['book_imgs']) == 2
    assert all(isinstance(book_img['id'], int) for book_img in response_data['data']['book_imgs'])
    assert response_data['data']['book_keywords'] == [
        {'id': 4, 'keyword': 'drama'},
        {'id': 5, 'keyword': 'máfia'},
        {'id': 6, 'keyword': 'itália'},
    ]
    assert response.status_code == 201


def test_when_try_to_create_book_without_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.post('/books', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'NoDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_create_book_with_invalid_name_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    invalid_data = {
        'price': 49.99,
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

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': '',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'Novo livro @#$123',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'aaa',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 456,
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
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
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': '',
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 490000.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.9999999999,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': -1,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 'abc',
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
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
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo 123 $%¨',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'aa',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': '',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
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
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': str(datetime.datetime.now().year + 1),
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': '123',
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 'abcd',
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': '',
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
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
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '100',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookKindDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': 'abc',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookKindDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookKindDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404


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
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '100',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookGenreDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': 'abc',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookGenreDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookGenreDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404


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
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': '',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia68;itáliaawdawdawdawdawdawdawd',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia#@;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-4.8mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
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
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/pdf-2mb.pdf', 'rb'), 'file.pdf'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png'),
            (open('tests/resources/img-11.3mb.png', 'rb'), 'image2.png'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': 'abc',
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {
        'name': 'O Poderoso Chefão',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [
            (open('tests/resources/text-2mb.txt', 'rb'), 'file.txt'),
        ],
    }

    response = client.post('/books', headers=headers, data=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_create_book_without_auth_returns_error_response(client: FlaskClient):
    response = client.post('/books')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_create_book_with_invalid_auth_returns_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    response = client.post('/books', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
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
        'imgs': [(open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')],
    }

    response = client.post('/books', headers=headers, data=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookAlreadyExists'
    assert response_data['status'] == 409
    assert response.status_code == 409

    data = {
        'name': ' o pequeno príncipe ',
        'price': 49.99,
        'author': 'Mario Puzo',
        'release_year': 1969,
        'id_book_kind': '1',
        'id_book_genre': '1',
        'keywords': 'drama;máfia;itália',
        'imgs': [(open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')],
    }

    response = client.post('/books', headers=headers, data=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookAlreadyExists'
    assert response_data['status'] == 409
    assert response.status_code == 409


def test_get_all_books(client: FlaskClient):
    response = client.get('/books')
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
            {
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
        ],
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_get_book_by_id(client: FlaskClient):
    book_id = 2

    response = client.get(f'/books/{book_id}')
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
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
    assert response.status_code == 200


def test_when_try_to_get_book_does_not_exists_return_error_response(client: FlaskClient):
    book_id = 100

    response = client.get(f'/books/{book_id}')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_delete_book(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 2

    response = client.delete(f'/books/{book_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {'error': False, 'status': 200}
    with app.app_context():
        assert not db.session.execute(
            text("SELECT COUNT(*) FROM book_imgs WHERE id_book = :id"), {'id': book_id}
        ).scalar()
        assert not db.session.execute(
            text("SELECT COUNT(*) FROM book_keywords WHERE id_book = :id"), {'id': book_id}
        ).scalar()

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_delete_book_does_not_exists_return_error_message(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 100

    response = client.delete(f'/books/{book_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_when_try_to_delete_book_without_auth_returns_error_response(client: FlaskClient):
    book_id = 2

    response = client.delete(f'/books/{book_id}')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_delete_book_with_invalid_auth_returns_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    book_id = 2

    response = client.delete(f'/books/{book_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_dump_Book_coming_from_db(app: Flask):
    with app.app_context():
        book = db.session.get(Book, 2)

        dump_book = books_schema.dump(book)

        expected_dump_book = {
            'id': 2,
            'name': 'Herdeiro do Império',
            'price': 89.67,
            'author': 'Timothy Zhan',
            'release_year': 1993,
            'book_kind': {'kind': 'físico', 'id': 1},
            'book_genre': {'genre': 'fábula', 'id': 1},
            'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
            'book_keywords': [{'id': 3, 'keyword': 'dramático'}],
        }

        assert dump_book == expected_dump_book


def test_update_name(client: FlaskClient, access_token: str):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2

    update = {'name': 'NOVO livro 123'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': {
            'id': 2,
            'name': 'NOVO livro 123',
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
    assert response.status_code == 200


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

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    update = {'name': 'abc'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    update = {'name': ''}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
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

    assert response_data['error']
    assert response_data['error_name'] == 'BookAlreadyExists'
    assert response_data['status'] == 409
    assert response.status_code == 409

    update = {'name': '  o pequeno prínCIpe '}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookAlreadyExists'
    assert response_data['status'] == 409
    assert response.status_code == 409


def test_update_price(client: FlaskClient, access_token: str):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2

    update = {'price': 1000}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': {
            'id': 2,
            'name': 'Herdeiro do Império',
            'price': 1000,
            'author': 'Timothy Zhan',
            'release_year': 1993,
            'book_kind': {'kind': 'físico', 'id': 1},
            'book_genre': {'genre': 'fábula', 'id': 1},
            'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
            'book_keywords': [{'id': 3, 'keyword': 'dramático'}],
        },
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_update_price_with_invalid_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2

    update = {'price': 1000000}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    update = {'price': 45.5646545}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    update = {'price': -27}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    update = {'price': ''}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_update_author(client: FlaskClient, access_token: str):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2

    update = {'author': 'William Shakespeare'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': {
            'id': 2,
            'name': 'Herdeiro do Império',
            'price': 89.67,
            'author': 'William Shakespeare',
            'release_year': 1993,
            'book_kind': {'kind': 'físico', 'id': 1},
            'book_genre': {'genre': 'fábula', 'id': 1},
            'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
            'book_keywords': [{'id': 3, 'keyword': 'dramático'}],
        },
    }

    assert response_data == expected_data
    assert response.status_code == 200


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

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    update = {'author': 'autor ¨%$'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    update = {'author': 'ab'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    update = {'author': ''}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_update_release_year(client: FlaskClient, access_token: str):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2

    update = {'release_year': 2014}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': {
            'id': 2,
            'name': 'Herdeiro do Império',
            'price': 89.67,
            'author': 'Timothy Zhan',
            'release_year': 2014,
            'book_kind': {'kind': 'físico', 'id': 1},
            'book_genre': {'genre': 'fábula', 'id': 1},
            'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
            'book_keywords': [{'id': 3, 'keyword': 'dramático'}],
        },
    }

    assert response_data == expected_data
    assert response.status_code == 200


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

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    update = {'release_year': 1700}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    update = {'release_year': -27}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    update = {'release_year': 'abc'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    update = {'release_year': ''}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_update_book_kind(client: FlaskClient, access_token: str):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2

    update = {'id_book_kind': 2}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': {
            'id': 2,
            'name': 'Herdeiro do Império',
            'price': 89.67,
            'author': 'Timothy Zhan',
            'release_year': 1993,
            'book_kind': {'kind': 'kindle', 'id': 2},
            'book_genre': {'genre': 'fábula', 'id': 1},
            'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
            'book_keywords': [{'id': 3, 'keyword': 'dramático'}],
        },
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_update_book_kind_with_invalid_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2

    update = {'id_book_kind': 2000000}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookKindDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404

    update = {'id_book_kind': 100}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookKindDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404

    update = {'id_book_kind': 'abc'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookKindDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404

    update = {'id_book_kind': ''}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookKindDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_update_book_genre(client: FlaskClient, access_token: str):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2

    update = {'id_book_genre': 2}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 200,
        'data': {
            'id': 2,
            'name': 'Herdeiro do Império',
            'price': 89.67,
            'author': 'Timothy Zhan',
            'release_year': 1993,
            'book_kind': {'kind': 'físico', 'id': 1},
            'book_genre': {'genre': 'ficção científica', 'id': 2},
            'book_imgs': [{'id': 2, 'img_url': 'http://localhost:5000/books/photos/test2.jpg'}],
            'book_keywords': [{'id': 3, 'keyword': 'dramático'}],
        },
    }

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_update_book_genre_with_invalid_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2

    update = {'id_book_genre': 2000000}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookGenreDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404

    update = {'id_book_genre': 100}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookGenreDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404

    update = {'id_book_genre': 'abc'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookGenreDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404

    update = {'id_book_genre': ''}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookGenreDoesntExists'
    assert response_data['status'] == 404
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

    assert response_data['error']
    assert response_data['error_name'] == 'NoDataSent'
    assert response_data['status'] == 400
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

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_update_book_without_auth_returns_error_response(client: FlaskClient):
    headers = {'Content-Type': 'multipart/form-data'}

    book_id = 2

    update = {'name': 'NOVO livro'}

    response = client.patch(f'/books/{book_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
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

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401
