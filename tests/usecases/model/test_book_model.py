from unittest.mock import Mock

import pytest

from model import Book


@pytest.fixture
def book() -> Book:
    return Book(Mock(), Mock(), Mock(), Mock())


def test_instantiate_Book():
    mock_name = Mock()
    mock_price = Mock()
    mock_author = Mock()
    mock_release_year = Mock()

    book = Book(mock_name, mock_price, mock_author, mock_release_year)

    assert book.id is None
    assert book.name == mock_name
    assert book.price == mock_price
    assert book.author == mock_author
    assert book.release_year == mock_release_year
    assert book.book_genre is None
    assert book.book_kind is None
    assert book.book_keywords == []
    assert book.book_imgs == []
    assert book.id_genre is None
    assert book.id_kind is None


def test_update_Book_name(book: Book):
    mock_name = Mock()
    book.update_name(mock_name)

    assert book.name == mock_name


def test_update_Book_price(book: Book):
    mock_price = Mock()
    book.update_price(mock_price)

    assert book.price == mock_price


def test_update_Book_author(book: Book):
    mock_author = Mock()
    book.update_author(mock_author)

    assert book.author == mock_author


def test_update_Book_release_year(book: Book):
    mock_release_year = Mock()
    book.update_release_year(mock_release_year)

    assert book.release_year == mock_release_year
