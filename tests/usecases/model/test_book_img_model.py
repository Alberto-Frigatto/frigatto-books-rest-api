from unittest.mock import Mock

import pytest

from model import BookImg


@pytest.fixture
def book_img() -> BookImg:
    return BookImg(Mock())


def test_instantiate_BookImg():
    mock_img = Mock()

    book_img = BookImg(mock_img)

    assert book_img.id is None
    assert book_img.img_url == mock_img


def test_update_BookImg_img_url(book_img: BookImg):
    mock_img = Mock()
    book_img.update_img_url(mock_img)

    assert book_img.img_url == mock_img
