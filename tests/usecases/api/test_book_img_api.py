import json
import os
import shutil
from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from app import create_app
from db import db
from model import BookImg, User


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
            text("INSERT INTO book_genres (genre) VALUES (:genre)"), {'genre': 'fábula'}
        )
        db.session.execute(text("INSERT INTO book_kinds (kind) VALUES (:kind)"), {'kind': 'físico'})

        db.session.execute(
            text(
                """--sql
                INSERT INTO books
                    (name, price, author, release_year, id_kind, id_genre)
                    VALUES (:name, :price, :author, :release_year, :id_kind, :id_genre)
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
                    'name': 'O Poderoso Chefão',
                    'price': 20.99,
                    'author': 'Mario Puzo',
                    'release_year': 1969,
                    'id_kind': 1,
                    'id_genre': 1,
                },
                {
                    'name': 'Livro',
                    'price': 20,
                    'author': 'Autor da Silva',
                    'release_year': 2000,
                    'id_kind': 1,
                    'id_genre': 1,
                },
            ],
        )

        db.session.execute(
            text("INSERT INTO book_imgs (img_url, id_book) VALUES (:img_url, :id_book)"),
            [
                {'img_url': 'http://localhost:5000/books/photos/test.jpg', 'id_book': 1},
                {'img_url': 'http://localhost:5000/books/photos/test2.jpg', 'id_book': 1},
                {'img_url': 'http://localhost:5000/books/photos/cat.jpg', 'id_book': 2},
                {'img_url': 'http://localhost:5000/books/photos/dog.jpg', 'id_book': 3},
                {'img_url': 'http://localhost:5000/books/photos/cow.jpg', 'id_book': 3},
                {'img_url': 'http://localhost:5000/books/photos/sheep.jpg', 'id_book': 3},
                {'img_url': 'http://localhost:5000/books/photos/pig.jpg', 'id_book': 3},
                {'img_url': 'http://localhost:5000/books/photos/horse.jpg', 'id_book': 3},
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


def test_get_book_img(client: FlaskClient):
    response = client.get('/books/photos/test.jpg')

    assert response.mimetype == 'image/jpeg'
    assert response.content_type == 'image/jpeg'
    assert response.content_length
    assert response.status_code == 200


def test_when_try_to_get_book_img_with_invalid_filename_returns_error_response(client: FlaskClient):
    filename = 'cat.jpg'
    response = client.get(f'/books/photos/{filename}')
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'ImageException',
        'code': 'ImageNotFound',
        'message': f'The image {filename} was not found',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_delete_book_img(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1
    img_id = 2

    response = client.delete(f'/books/{book_id}/photos/{img_id}', headers=headers)

    assert not response.data
    assert response.status_code == 204

    with app.app_context():
        book_img = db.session.get(BookImg, img_id)

        assert book_img is None

    assert 'test2.jpg' not in os.listdir('tests/uploads')


def test_when_try_to_delete_last_book_img_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 2
    img_id = 3

    response = client.delete(f'/books/{book_id}/photos/{img_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookImgException',
        'code': 'BookMustHaveAtLeastOneImg',
        'message': f'The book {book_id} must have at least one image',
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_delete_book_img_does_not_exists_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1
    img_id = 100

    response = client.delete(f'/books/{book_id}/photos/{img_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookImgException',
        'code': 'BookImgDoesntExists',
        'message': f'The image {img_id} does not exist',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_when_try_to_delete_book_img_from_book_does_not_exists_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 100
    img_id = 2

    response = client.delete(f'/books/{book_id}/photos/{img_id}', headers=headers)
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


def test_when_try_to_delete_book_img_from_book_does_not_own_it_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 2
    img_id = 2

    response = client.delete(f'/books/{book_id}/photos/{img_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookImgException',
        'code': 'BookDoesntOwnThisImg',
        'message': f'The image {img_id} does not belong to the book {book_id}',
        'status': 401,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 401


def test_when_try_to_delete_book_img_without_auth_returns_error_response(client: FlaskClient):
    book_id = 1
    img_id = 2

    response = client.delete(f'/books/{book_id}/photos/{img_id}')
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


def test_when_try_to_delete_book_img_with_invalid_auth_returns_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    book_id = 1
    img_id = 2

    response = client.delete(f'/books/{book_id}/photos/{img_id}', headers=headers)
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


def test_update_book_img(client: FlaskClient, access_token: str, app: Flask):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 1
    img_id = 2

    update = {'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')}

    response = client.patch(f'/books/{book_id}/photos/{img_id}', headers=headers, data=update)
    response_data: dict = json.loads(response.data)

    expected_data = {
        'id': img_id,
    }

    assert response_data['id'] == expected_data['id']

    original_img_url = 'http://localhost:5000/users/photos/test2.jpg'
    assert response_data['img_url']
    assert isinstance(response_data['img_url'], str)
    assert response_data['img_url'].startswith('http://localhost:5000/books/photos/')
    assert response_data['img_url'].endswith('.jpg')
    assert response_data['img_url'] != original_img_url
    assert response.status_code == 200

    dir = 'tests/uploads'

    assert 'test2.jpg' not in os.listdir(dir)

    for filename in os.listdir(dir):
        if filename != 'test.jpg':
            assert os.path.isfile(os.path.join(dir, filename))

    with app.app_context():
        book_img = db.session.get(BookImg, img_id)

        assert book_img is not None
        assert book_img.id == img_id
        assert book_img.img_url != original_img_url
        assert book_img.id_book == book_id


def test_when_try_to_update_book_img_does_not_exists_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 1
    img_id = 100

    update = {'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')}

    response = client.patch(f'/books/{book_id}/photos/{img_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookImgException',
        'code': 'BookImgDoesntExists',
        'message': f'The image {img_id} does not exist',
        'status': 404,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 404


def test_when_try_to_update_book_img_from_book_does_not_exists_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 100
    img_id = 1

    update = {'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')}

    response = client.patch(f'/books/{book_id}/photos/{img_id}', headers=headers, data=update)
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


def test_when_try_to_update_book_img_without_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 1
    img_id = 2

    response = client.patch(f'/books/{book_id}/photos/{img_id}', headers=headers)
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


def test_when_try_to_update_book_img_with_invalid_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 1
    img_id = 2

    update = {'img': (open('tests/resources/img-11.3mb.png', 'rb'), 'image.png')}

    response = client.patch(f'/books/{book_id}/photos/{img_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['img'],
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

    update = {'imgs': (open('tests/resources/img-417kb.png', 'rb'), 'image.png')}

    response = client.patch(f'/books/{book_id}/photos/{img_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['img'], 'msg': 'Field required', 'type': 'missing'},
            {'loc': ['imgs'], 'msg': 'Extra inputs are not permitted', 'type': 'extra_forbidden'},
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'img': 'abc'}

    response = client.patch(f'/books/{book_id}/photos/{img_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['img'],
                'msg': 'Value error, The provided image is not a file',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    update = {'img': (open('tests/resources/pdf-2mb.pdf', 'rb'), 'pdf.pdf')}

    response = client.patch(f'/books/{book_id}/photos/{img_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['img'],
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


def test_when_try_to_update_book_img_from_book_does_not_own_it_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 2
    img_id = 2

    update = {'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')}

    response = client.patch(f'/books/{book_id}/photos/{img_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookImgException',
        'code': 'BookDoesntOwnThisImg',
        'message': f'The image {img_id} does not belong to the book {book_id}',
        'status': 401,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 401


def test_when_try_to_update_book_img_without_auth_returns_error_response(client: FlaskClient):
    book_id = 1
    img_id = 2

    update = {'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')}

    response = client.patch(f'/books/{book_id}/photos/{img_id}', data=update)
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


def test_when_try_to_update_book_img_with_invalid_auth_returns_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    book_id = 1
    img_id = 2

    update = {'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')}

    response = client.patch(f'/books/{book_id}/photos/{img_id}', headers=headers, data=update)
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


def test_add_book_img(client: FlaskClient, access_token: str, app: Flask):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    data = {'img': (open('tests/resources/img-417kb.png', 'rb'), 'image.png')}
    book_id = 1

    response = client.post(f'/books/{book_id}/photos', headers=headers, data=data)
    response_data: dict = json.loads(response.data)

    expected_data = {'id': 9}

    assert response_data['id'] == expected_data['id']
    assert response_data['img_url']
    assert isinstance(response_data['img_url'], str)
    assert response_data['img_url'].startswith('http://localhost:5000/books/photos/')
    assert response_data['img_url'].endswith('.jpg')
    assert response.status_code == 201

    dir = 'tests/uploads'
    for filename in os.listdir(dir):
        if filename not in ('test.jpg', 'test2.jpg'):
            assert os.path.isfile(os.path.join(dir, filename))

    with app.app_context():
        book_img = db.session.get(BookImg, expected_data['id'])

        assert book_img is not None
        assert book_img.id == expected_data['id']
        assert book_img.img_url.startswith('http://localhost:5000/books/photos/')
        assert book_img.img_url.endswith('.jpg')
        assert book_img.id_book == book_id


def test_when_try_to_add_an_image_to_a_book_with_5_images_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 3
    data = {'img': (open('tests/resources/img-417kb.png', 'rb'), 'image.png')}

    response = client.post(f'/books/{book_id}/photos', headers=headers, data=data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'BookImgException',
        'code': 'BookAlreadyHaveImageMaxQty',
        'message': 'The book "Livro" already have the max quantity of images',
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400


def test_when_try_to_create_book_img_from_book_does_not_exists_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 100

    data = {'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')}

    response = client.post(f'/books/{book_id}/photos', headers=headers, data=data)
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


def test_when_try_to_create_book_img_without_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 1

    response = client.post(f'/books/{book_id}/photos', headers=headers)
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


def test_when_try_to_create_book_img_with_invalid_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 1

    data = {'img': (open('tests/resources/img-11.3mb.png', 'rb'), 'image.png')}

    response = client.post(f'/books/{book_id}/photos', headers=headers, data=data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['img'],
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

    data = {'imgs': (open('tests/resources/img-417kb.png', 'rb'), 'image.png')}

    response = client.post(f'/books/{book_id}/photos', headers=headers, data=data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {'loc': ['img'], 'msg': 'Field required', 'type': 'missing'},
            {'loc': ['imgs'], 'msg': 'Extra inputs are not permitted', 'type': 'extra_forbidden'},
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    data = {'img': 'abc'}

    response = client.post(f'/books/{book_id}/photos', headers=headers, data=data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['img'],
                'msg': 'Value error, The provided image is not a file',
                'type': 'value_error',
            }
        ],
        'status': 400,
    }

    for key, value in expected_data.items():
        assert response_data[key] == value

    assert datetime.fromisoformat(response_data['timestamp'])
    assert response.status_code == 400

    data = {'img': (open('tests/resources/pdf-2mb.pdf', 'rb'), 'pdf.pdf')}

    response = client.post(f'/books/{book_id}/photos', headers=headers, data=data)
    response_data = json.loads(response.data)

    expected_data = {
        'scope': 'GeneralException',
        'code': 'InvalidDataSent',
        'message': 'Invalid data sent',
        'detail': [
            {
                'loc': ['img'],
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


def test_when_try_to_create_book_img_without_auth_returns_error_response(client: FlaskClient):
    book_id = 1

    data = {'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')}

    response = client.post(f'/books/{book_id}/photos', data=data)
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


def test_when_try_to_create_book_img_with_invalid_auth_returns_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    book_id = 1

    data = {'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')}

    response = client.post(f'/books/{book_id}/photos', headers=headers, data=data)
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
