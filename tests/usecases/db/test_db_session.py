from typing import Sequence
from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import Select, select
from sqlalchemy.orm import scoped_session

from app import create_app
from db.impl import DbSession
from exception import GeneralException
from model import Book


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_query(app: Flask) -> Select:
    with app.app_context():
        return select(Book)


@pytest.fixture
def mock_sql_alchemy() -> Mock:
    mock_sql_alchemy = create_autospec(SQLAlchemy)
    mock_sql_alchemy.session = create_autospec(scoped_session)

    return mock_sql_alchemy


@pytest.fixture
def db_session(mock_sql_alchemy: Mock) -> DbSession:
    return DbSession(mock_sql_alchemy)


def test_get_all_models(
    db_session: DbSession,
    app: Flask,
    mock_sql_alchemy: Mock,
    mock_query: Select,
):
    with app.app_context():
        mock_pagination = Mock(Pagination)
        mock_pagination.items = [Mock(Book) for _ in range(10)]
        mock_pagination.total = len(mock_pagination.items)
        mock_pagination.page = 1
        mock_pagination.pages = 1
        mock_pagination.per_page = 20
        mock_pagination.has_prev = False
        mock_pagination.has_next = False
        mock_pagination.prev_num = None
        mock_pagination.next_num = None

        mock_sql_alchemy.paginate = Mock(return_value=mock_pagination)

        page = 1
        result = db_session.paginate(mock_query, page=page)

        assert isinstance(result, Pagination)
        assert result.items == mock_pagination.items
        assert result.total == mock_pagination.total
        assert result.page == mock_pagination.page
        assert result.pages == mock_pagination.pages
        assert result.per_page == mock_pagination.per_page
        assert result.has_prev == mock_pagination.has_prev
        assert result.has_next == mock_pagination.has_next
        assert result.prev_num == mock_pagination.prev_num
        assert result.next_num == mock_pagination.next_num

        mock_sql_alchemy.paginate.assert_called_once_with(
            mock_query,
            page=page,
            per_page=20,
        )


def test_when_try_to_get_all_models_with_page_does_not_exists_raises_PaginationPageDoesNotExists(
    db_session: DbSession,
    app: Flask,
    mock_sql_alchemy: Mock,
    mock_query: Select,
):
    with app.app_context(), pytest.raises(GeneralException.PaginationPageDoesNotExists):
        page = 1
        mock_sql_alchemy.paginate = Mock(
            side_effect=GeneralException.PaginationPageDoesNotExists(page)
        )

        db_session.paginate(mock_query, page=page)


def test_get_model_by_id_returns_model(
    db_session: DbSession,
    app: Flask,
    mock_sql_alchemy: Mock,
):
    with app.app_context():
        mock_model = Mock(Book)
        mock_sql_alchemy.session.get = Mock(return_value=mock_model)

        model_id = '1'
        result = db_session.get_by_id(Book, model_id)

        assert isinstance(result, Book)
        assert result == mock_model

        mock_sql_alchemy.session.get.assert_called_once_with(Book, model_id)


def test_get_model_by_id_returns_None(
    db_session: DbSession,
    app: Flask,
    mock_sql_alchemy: Mock,
):
    with app.app_context():
        mock_sql_alchemy.session.get = Mock(return_value=None)

        model_id = '1'
        result = db_session.get_by_id(Book, model_id)

        assert result is None

        mock_sql_alchemy.session.get.assert_called_once_with(Book, model_id)


def test_get_one_model_returns_model(
    db_session: DbSession, app: Flask, mock_sql_alchemy: Mock, mock_query: Mock
):
    with app.app_context():
        mock_model = Mock(Book)
        mock_scalar = Mock()
        mock_scalar.scalar = Mock(return_value=mock_model)

        mock_sql_alchemy.session.execute = Mock(return_value=mock_scalar)

        result = db_session.get_one(mock_query)

        assert isinstance(result, Book)
        assert result == mock_model

        mock_sql_alchemy.session.execute.assert_called_once_with(mock_query)
        mock_scalar.scalar.assert_called_once()


def test_get_one_model_returns_None(
    db_session: DbSession, app: Flask, mock_sql_alchemy: Mock, mock_query: Mock
):
    with app.app_context():
        mock_scalar = Mock()
        mock_scalar.scalar = Mock(return_value=None)

        mock_sql_alchemy.session.execute = Mock(return_value=mock_scalar)

        result = db_session.get_one(mock_query)

        assert result is None

        mock_sql_alchemy.session.execute.assert_called_once_with(mock_query)
        mock_scalar.scalar.assert_called_once()


def test_get_many_models_returns_models(
    db_session: DbSession, app: Flask, mock_sql_alchemy: Mock, mock_query: Mock
):
    with app.app_context():
        mock_models = [Mock(Book) for _ in range(4)]
        mock_all = Mock()
        mock_all.all = Mock(return_value=mock_models)

        mock_scalars = Mock()
        mock_scalars.scalars = Mock(return_value=mock_all)

        mock_sql_alchemy.session.execute = Mock(return_value=mock_scalars)

        result = db_session.get_many(mock_query)

        assert isinstance(result, Sequence)
        assert result == mock_models

        mock_sql_alchemy.session.execute.assert_called_once_with(mock_query)
        mock_scalars.scalars.assert_called_once()
        mock_all.all.assert_called_once()


def test_get_many_models_returns_empty_sequence(
    db_session: DbSession, app: Flask, mock_sql_alchemy: Mock, mock_query: Mock
):
    with app.app_context():
        mock_models = []
        mock_all = Mock()
        mock_all.all = Mock(return_value=mock_models)

        mock_scalars = Mock()
        mock_scalars.scalars = Mock(return_value=mock_all)

        mock_sql_alchemy.session.execute = Mock(return_value=mock_scalars)

        result = db_session.get_many(mock_query)

        assert isinstance(result, Sequence)
        assert result == mock_models

        mock_sql_alchemy.session.execute.assert_called_once_with(mock_query)
        mock_scalars.scalars.assert_called_once()
        mock_all.all.assert_called_once()


def test_update_model(db_session: DbSession, app: Flask, mock_sql_alchemy: Mock):
    with app.app_context():
        result = db_session.update()

        assert result is None

        mock_sql_alchemy.session.commit.assert_called_once()


def test_add_model(db_session: DbSession, app: Flask, mock_sql_alchemy: Mock, mock_query: Mock):
    with app.app_context():
        mock_model = Mock(Book)
        result = db_session.add(mock_model)

        assert result is None

        mock_sql_alchemy.session.add.assert_called_once_with(mock_model)
        mock_sql_alchemy.session.commit.assert_called_once()


def test_delete_model(db_session: DbSession, app: Flask, mock_sql_alchemy: Mock, mock_query: Mock):
    with app.app_context():
        mock_model = Mock(Book)
        result = db_session.delete(mock_model)

        assert result is None

        mock_sql_alchemy.session.delete.assert_called_once_with(mock_model)
        mock_sql_alchemy.session.commit.assert_called_once()
