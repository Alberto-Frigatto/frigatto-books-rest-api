from unittest.mock import Mock

import pytest

from model import BookKind


@pytest.fixture
def book_kind() -> BookKind:
    return BookKind(Mock())


def test_instantiate_BookKind():
    mock_kind = Mock()

    book_kind = BookKind(mock_kind)

    assert book_kind.id is None
    assert book_kind.kind == mock_kind


def test_update_BookKind_kind(book_kind: BookKind):
    mock_kind = Mock()
    book_kind.update_kind(mock_kind)

    assert book_kind.kind == mock_kind
