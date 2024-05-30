import json

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from sqlalchemy import text

from app import create_app
from db import db
from exception import GeneralException
from model import BookKeyword, User
from schema.book_keywords_schema import BookKeywordsSchema


@pytest.fixture()
def app():
    app = create_app(True)

    with app.app_context():
        db.create_all()

        db.session.execute(
            text(
                f"""
                INSERT INTO users (username, password, img_url)
                    VALUES ('test', 'Senha@123', 'http://localhost:5000/users/keywords/test.jpg')
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
                INSERT INTO book_keywords
                    (keyword, id_book)
                    VALUES
                        ('dramático', 1),
                        ('infantil', 1),
                        ('máfia', 2)
            """
            )
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


def test_instantiate_BookKeyword():
    keyword = 'palavra chave'
    book_keyword = BookKeyword(keyword)

    assert book_keyword.keyword == keyword


def test_instantiate_BookKeyword_with_uppercase_keyword():
    keyword = 'PALAVRA CHAVE'
    book_keyword = BookKeyword(keyword)

    assert book_keyword.keyword == keyword.lower()


def test_when_BookKeyword_receives_invalid_keyword_raises_InvalidDataSent():
    with pytest.raises(GeneralException.InvalidDataSent):
        BookKeyword('')

    with pytest.raises(GeneralException.InvalidDataSent):
        BookKeyword('12')

    with pytest.raises(GeneralException.InvalidDataSent):
        BookKeyword('#')

    with pytest.raises(GeneralException.InvalidDataSent):
        BookKeyword('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')

    with pytest.raises(GeneralException.InvalidDataSent):
        BookKeyword(None)

    with pytest.raises(GeneralException.InvalidDataSent):
        BookKeyword(123)


def test_dump_BookKeyword_coming_from_db(app: Flask):
    with app.app_context():
        book_keyword = db.session.get(BookKeyword, 1)

        dump_book_keyword = BookKeywordsSchema().dump(book_keyword)

        expected_dump_book_keyword = {'id': 1, 'keyword': 'dramático'}

        assert dump_book_keyword == expected_dump_book_keyword


def test_add_book_keyword_in_lowercase(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1

    data = {'keyword': 'emocionante'}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=data)
    response_data = json.loads(response.data)

    expected_data = {'error': False, 'status': 201, 'data': {'id': 4, 'keyword': 'emocionante'}}

    assert response_data == expected_data
    assert response.status_code == 201


def test_add_book_keyword_with_space_and_in_uppercase(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1

    data = {'keyword': ' MUITO EMOCIONANTE'}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=data)
    response_data = json.loads(response.data)

    expected_data = {
        'error': False,
        'status': 201,
        'data': {'id': 4, 'keyword': 'muito emocionante'},
    }

    assert response_data == expected_data
    assert response.status_code == 201


def test_when_try_to_add_book_keyword_with_invalid_data(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1

    invalid_data = {'keyword': ''}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {'keyword': '  '}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {'keyword': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {'keyword': 'adwa234@#$@#$as'}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {'keyword': 456}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400

    invalid_data = {'keywords': 'teste'}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=invalid_data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_add_book_keyword_without_data(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1

    response = client.post(f'/books/{book_id}/keywords', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'NoDataSent'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_add_book_keyword_with_content_type_multipart_form_data_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data',
    }

    book_id = 1

    data = {'keyword': 'palavra'}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, data=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidContentType'
    assert response_data['status'] == 415
    assert response.status_code == 415


def test_when_try_to_add_book_keyword_without_auth_return_error_response(client: FlaskClient):
    book_id = 1

    data = {'keyword': 'palavra'}

    response = client.post(f'/books/{book_id}/keywords', json=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_add_book_keyword_with_invalid_auth_return_error_response(client: FlaskClient):
    headers = {'Authorization': f'Bearer 123'}

    book_id = 1

    data = {'keyword': 'palavra'}

    response = client.post(f'/books/{book_id}/keywords', headers=headers, json=data)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_delete_book_keyword(client: FlaskClient, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1
    book_keyword_id = 2

    response = client.delete(f'/books/{book_id}/keywords/{book_keyword_id}', headers=headers)
    response_data = json.loads(response.data)

    expected_data = {'error': False, 'status': 200}

    assert response_data == expected_data
    assert response.status_code == 200


def test_when_try_to_delete_book_keyword_without_auth_return_error_response(client: FlaskClient):
    headers = {'Content-Type': 'application/json'}

    book_id = 1
    book_keyword_id = 2

    response = client.delete(f'/books/{book_id}/keywords/{book_keyword_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'MissingJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_delete_book_keyword_with_invalid_auth_return_error_response(
    client: FlaskClient,
):
    headers = {
        'Authorization': f'Bearer 123',
        'Content-Type': 'application/json',
    }

    book_id = 1
    book_keyword_id = 2

    response = client.delete(f'/books/{book_id}/keywords/{book_keyword_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'InvalidJWT'
    assert response_data['status'] == 401
    assert response.status_code == 401


def test_when_try_to_delete_last_book_keyword_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 2
    book_keyword_id = 3

    response = client.delete(f'/books/{book_id}/keywords/{book_keyword_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookMustHaveAtLeastOneKeyword'
    assert response_data['status'] == 400
    assert response.status_code == 400


def test_when_try_to_delete_book_keyword_does_not_exists_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 1
    book_keyword_id = 100

    response = client.delete(f'/books/{book_id}/keywords/{book_keyword_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookKeywordDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_when_try_to_delete_book_keyword_from_book_does_not_exists_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 100
    book_keyword_id = 2

    response = client.delete(f'/books/{book_id}/keywords/{book_keyword_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookDoesntExists'
    assert response_data['status'] == 404
    assert response.status_code == 404


def test_when_try_to_delete_book_keyword_from_book_does_not_own_it_returns_error_response(
    client: FlaskClient, access_token: str
):
    headers = {'Authorization': f'Bearer {access_token}'}

    book_id = 2
    book_keyword_id = 2

    response = client.delete(f'/books/{book_id}/keywords/{book_keyword_id}', headers=headers)
    response_data = json.loads(response.data)

    assert response_data['error']
    assert response_data['error_name'] == 'BookDoesntOwnThisKeyword'
    assert response_data['status'] == 401
    assert response.status_code == 401
