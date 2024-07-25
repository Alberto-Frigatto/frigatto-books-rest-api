from unittest.mock import Mock

import pytest

from model import BookGenre


@pytest.fixture
def book_genre() -> BookGenre:
    return BookGenre(Mock())


def test_instantiate_BookGenre():
    mock_genre = Mock()

    book_genre = BookGenre(mock_genre)

    assert book_genre.id is None
    assert book_genre.genre == mock_genre


def test_update_BookGenre_genre(book_genre: BookGenre):
    mock_genre = Mock()
    book_genre.update_genre(mock_genre)

    assert book_genre.genre == mock_genre
