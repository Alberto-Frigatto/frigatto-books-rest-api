from unittest.mock import Mock

from model import BookKeyword


def test_instantiate_BookKeyword():
    mock_keyword = Mock()

    book_keyword = BookKeyword(mock_keyword)

    assert book_keyword.id is None
    assert book_keyword.keyword == mock_keyword
