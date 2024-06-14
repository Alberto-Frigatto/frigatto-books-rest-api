import json
import os
import shutil

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from sqlalchemy import text

from app import create_app
from db import db
from model import BookImg, User
from schema.book_imgs_schema import BookImgsSchema


@pytest.fixture()
def app():
    app = create_app(True)

    with app.app_context():
        db.create_all()

        db.session.execute(
            text(
                f"""
                INSERT INTO users (username, password, img_url)
                    VALUES ('test', 'Senha@123', 'http://localhost:5000/users/photos/test.jpg')
                """
            )
        )

        db.session.execute(text("INSERT INTO book_genres (genre) VALUES ('fábula')"))
        db.session.execute(text("INSERT INTO book_kinds (kind) VALUES ('físico')"))

        db.session.execute(
            text(
                """
                INSERT INTO books
                    (name, price, author, release_year, id_kind, id_genre)
                    VALUES
                        ('O Pequeno Príncipe', 10.99, 'Antoine de Saint-Exupéry', 1943, 1, 1),
                        ('O Poderoso Chefão', 20.99, 'Mario Puzo', 1969, 1, 1)
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
                        ('http://localhost:5000/books/photos/test2.jpg', 1),
                        ('http://localhost:5000/books/photos/cat.jpg', 2)
                """
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


def test_instantiate_BookImg():
    img_url = 'http://localhost:5000/books/photos/test.jpg'
    book_img = BookImg(img_url)

    assert book_img.img_url == img_url


def test_dump_BookImg_coming_from_db(app: Flask):
    with app.app_context():
        book_img = db.session.get(BookImg, 1)

        dump_book_img = BookImgsSchema().dump(book_img)

        expected_dump_book_img = {'id': 1, 'img_url': 'http://localhost:5000/books/photos/test.jpg'}

        assert dump_book_img == expected_dump_book_img


def test_get_book_img(client: FlaskClient):
    response = client.get(f'/books/photos/test.jpg')

    assert response.mimetype == 'image/jpeg'
    assert response.content_type == 'image/jpeg'
    assert response.content_length
    assert response.status_code == 200


def test_when_try_to_get_book_img_with_invalid_filename_returns_error_response(client: FlaskClient):
    response = client.get(f'/books/photos/cat.jpg')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'ImageNotFound'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_delete_book_img(client: FlaskClient, access_token: str, app: Flask):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1
    img_id = 2

    response = client.delete(f'/books/{book_id}/photos/{img_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {'error': False, 'status': 200}

    assert response_data == expected_data
    assert response.status_code == 200

    with app.app_context():
        book_img = db.session.get(BookImg, 2)

        assert book_img is None


def test_when_try_to_delete_last_book_img_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 2
    img_id = 3

    response = client.delete(f'/books/{book_id}/photos/{img_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookMustHaveAtLeastOneImg'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_delete_book_img_does_not_exists_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1
    img_id = 100

    response = client.delete(f'/books/{book_id}/photos/{img_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookImgDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_when_try_to_delete_book_img_from_book_does_not_exists_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 100
    img_id = 2

    response = client.delete(f'/books/{book_id}/photos/{img_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_when_try_to_delete_book_img_from_book_does_not_own_it_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 2
    img_id = 2

    response = client.delete(f'/books/{book_id}/photos/{img_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookDoesntOwnThisImg'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_delete_book_img_without_auth_returns_error_response(client: FlaskClient):
    book_id = 1
    img_id = 2

    response = client.delete(f'/books/{book_id}/photos/{img_id}')
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_delete_book_img_with_invalid_auth_returns_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    book_id = 1
    img_id = 2

    response = client.delete(f'/books/{book_id}/photos/{img_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
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
    response_data = json.loads(response.data)

    assert not response_data['error']
    assert response_data['status'] == 200
    assert response_data['data']
    assert response_data['data']['id'] == 2
    assert response_data['data']['img_url'] != 'http://localhost:5000/users/photos/test2.jpg'
    assert response.status_code == 200

    with app.app_context():
        book_img = db.session.get(BookImg, 2)

        assert book_img is not None
        assert book_img.id == 2
        assert book_img.img_url != 'http://localhost:5000/users/photos/test2.jpg'
        assert book_img.id_book == 1


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

    assert response_data['error']
    assert response_data['error_name'] == 'BookImgDoesntExists'
    assert response_data['status'] == 404
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

    assert response_data['error']
    assert response_data['error_name'] == 'BookDoesntExists'
    assert response_data['status'] == 404
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

    assert response_data['error']
    assert response_data['error_name'] == 'NoDataSent'
    assert response_data['status'] == 400
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

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    update = {'imgs': (open('tests/resources/img-11.3mb.png', 'rb'), 'image.png')}

    response = client.patch(f'/books/{book_id}/photos/{img_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    update = {'img': 'abc'}

    response = client.patch(f'/books/{book_id}/photos/{img_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    update = {'img': (open('tests/resources/pdf-2mb.pdf', 'rb'), 'pdf.pdf')}

    response = client.patch(f'/books/{book_id}/photos/{img_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
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

    assert response_data['error']
    assert response_data['error_name'] == 'BookDoesntOwnThisImg'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_update_book_img_without_auth_returns_error_response(client: FlaskClient):
    book_id = 1
    img_id = 2

    update = {'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')}

    response = client.patch(f'/books/{book_id}/photos/{img_id}', data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_update_book_img_with_invalid_auth_returns_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    book_id = 1
    img_id = 2

    update = {'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')}

    response = client.patch(f'/books/{book_id}/photos/{img_id}', headers=headers, data=update)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_add_book_img(client: FlaskClient, access_token: str, app: Flask):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 1

    data = {'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')}

    response = client.post(f'/books/{book_id}/photos', headers=headers, data=data)
    response_data = json.loads(response.data)

    assert not response_data['error']
    assert response_data['status'] == 201
    assert response_data['data']
    assert response_data['data']['id'] == 4
    assert response_data['data']['img_url'].startswith('http://localhost:5000/books/photos/')
    assert response_data['data']['img_url'].endswith('.jpg')
    assert response.status_code == 201

    with app.app_context():
        book_img = db.session.get(BookImg, 4)

        assert book_img is not None
        assert book_img.id == 4
        assert book_img.img_url.startswith('http://localhost:5000/books/photos/')
        assert book_img.img_url.endswith('.jpg')
        assert book_img.id_book == 1


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

    assert response_data['error']
    assert response_data['error_name'] == 'BookDoesntExists'
    assert response_data['status'] == 404
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

    assert response_data['error']
    assert response_data['error_name'] == 'NoDataSent'
    assert response_data['status'] == 400
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

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    data = {'imgs': (open('tests/resources/img-11.3mb.png', 'rb'), 'image.png')}

    response = client.post(f'/books/{book_id}/photos', headers=headers, data=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    data = {'img': 'abc'}

    response = client.post(f'/books/{book_id}/photos', headers=headers, data=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    data = {'img': (open('tests/resources/pdf-2mb.pdf', 'rb'), 'pdf.pdf')}

    response = client.post(f'/books/{book_id}/photos', headers=headers, data=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_create_book_img_without_auth_returns_error_response(client: FlaskClient):
    book_id = 1

    data = {'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')}

    response = client.post(f'/books/{book_id}/photos', data=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_create_book_img_with_invalid_auth_returns_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    book_id = 1

    data = {'img': (open('tests/resources/img-1.1mb.png', 'rb'), 'image.png')}

    response = client.post(f'/books/{book_id}/photos', headers=headers, data=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401
