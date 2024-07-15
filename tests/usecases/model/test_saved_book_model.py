from unittest.mock import Mock

from model import SavedBook


def test_instantiate_SavedBook():
    mock_id_user = Mock()
    mock_book = Mock()

    saved_book = SavedBook(mock_id_user, mock_book)

    assert saved_book.id is None
    assert saved_book.id_user == mock_id_user
    assert saved_book.book == mock_book
