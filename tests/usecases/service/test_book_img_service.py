from unittest.mock import Mock, create_autospec, patch

import pytest
from flask import Flask

from app import create_app
from dto.input import BookImgInputDTO
from exception import BookImgException, ImageException
from model import Book, BookImg
from repository import IBookImgRepository, IBookRepository
from service.impl import BookImgService
from utils.file.uploader import BookImageUploader


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_book_img_repository() -> Mock:
    return create_autospec(IBookImgRepository)


@pytest.fixture
def mock_book_repository() -> Mock:
    return create_autospec(IBookRepository)


@pytest.fixture
def book_img_service(mock_book_repository: Mock, mock_book_img_repository: Mock) -> BookImgService:
    return BookImgService(mock_book_repository, mock_book_img_repository)


def test_get_book_photo(
    book_img_service: BookImgService,
    app: Flask,
):
    with app.app_context():
        result = book_img_service.get_book_photo('test.jpg')

        assert isinstance(result, tuple)

        file_path, mimetype = result

        assert file_path == 'tests/uploads/test.jpg'
        assert mimetype == 'image/jpeg'


def test_when_try_to_get_book_photo_with_filename_does_not_exists_raises_ImageNotFound(
    book_img_service: BookImgService,
    app: Flask,
):
    with pytest.raises(ImageException.ImageNotFound):
        with app.app_context():
            book_img_service.get_book_photo('image_doesnt_exists.jpg')


def test_add_book_img_to_a_book(
    book_img_service: BookImgService,
    app: Flask,
    mock_book_repository: Mock,
    mock_book_img_repository: Mock,
):
    with app.app_context():
        mock_dto = create_autospec(BookImgInputDTO)
        mock_dto.img = create_autospec(BookImageUploader)
        mock_dto.img.get_url = Mock(return_value='http://localhost/books/photos/new_image.jpg')

        book_id = '1'

        mock_book = Mock(Book)
        mock_book.id = int(book_id)
        mock_book.book_imgs = [Mock(BookImg) for _ in range(3)]

        mock_book_repository.get_by_id = Mock(return_value=mock_book)

        result = book_img_service.create_book_img(book_id, mock_dto)

        mock_dto.img.get_url.assert_called_once()
        mock_dto.img.save.assert_called_once()
        mock_book_repository.get_by_id.assert_called_once_with(book_id)
        mock_book_img_repository.add.assert_called_once_with(result)

        assert isinstance(result, BookImg)
        assert result.id_book == mock_book.id
        assert result.img_url == mock_dto.img.get_url()


def test_when_try_to_add_book_img_to_a_book_with_max_qty_imgs_raises_BookAlreadyHaveImageMaxQty(
    book_img_service: BookImgService,
    app: Flask,
    mock_book_repository: Mock,
):
    with pytest.raises(BookImgException.BookAlreadyHaveImageMaxQty), app.app_context():
        mock_dto = create_autospec(BookImgInputDTO)
        mock_dto.img = create_autospec(BookImageUploader)
        mock_dto.img.get_url = Mock(return_value='http://localhost/books/photos/new_image.jpg')

        book_id = '1'

        mock_book = Mock(Book)
        mock_book.id = int(book_id)
        mock_book.book_imgs = [Mock(BookImg) for _ in range(5)]

        mock_book_repository.get_by_id = Mock(return_value=mock_book)

        book_img_service.create_book_img(book_id, mock_dto)


def test_delete_book_img_from_a_book(
    book_img_service: BookImgService,
    app: Flask,
    mock_book_repository: Mock,
    mock_book_img_repository: Mock,
):
    with app.app_context():
        book_id = '1'

        mock_book = Mock(Book)
        mock_book.id = int(book_id)
        mock_book.book_imgs = [Mock(BookImg) for _ in range(3)]

        mock_book_repository.get_by_id = Mock(return_value=mock_book)

        book_img_id = '1'

        mock_book_img = Mock(BookImg)
        mock_book_img.id = int(book_img_id)
        mock_book_img.id_book = mock_book.id

        mock_book_img_repository.get_by_id = Mock(return_value=mock_book_img)

        result = book_img_service.delete_book_img(book_id, book_img_id)

        mock_book_repository.get_by_id.assert_called_once_with(book_id)
        mock_book_img_repository.get_by_id.assert_called_once_with(book_img_id)
        mock_book_img_repository.delete.assert_called_once_with(mock_book_img)

        assert result is None


def test_when_try_to_delete_book_img_from_a_book_doesnt_own_this_image_raises_BookDoesntOwnThisImg(
    book_img_service: BookImgService,
    app: Flask,
    mock_book_repository: Mock,
    mock_book_img_repository: Mock,
):
    with pytest.raises(BookImgException.BookDoesntOwnThisImg), app.app_context():
        book_id = '1'

        mock_book = Mock(Book)
        mock_book.id = int(book_id)

        mock_book_repository.get_by_id = Mock(return_value=mock_book)

        book_img_id = '1'

        mock_book_img = Mock(BookImg)
        mock_book_img.id = int(book_img_id)
        mock_book_img.id_book = 2

        mock_book_img_repository.get_by_id = Mock(return_value=mock_book_img)

        book_img_service.delete_book_img(book_id, book_img_id)


def test_when_try_to_delete_the_last_book_img_from_a_book_raises_BookMustHaveAtLeastOneImg(
    book_img_service: BookImgService,
    app: Flask,
    mock_book_repository: Mock,
    mock_book_img_repository: Mock,
):
    with pytest.raises(BookImgException.BookMustHaveAtLeastOneImg), app.app_context():
        book_id = '1'

        mock_book = Mock(Book)
        mock_book.id = int(book_id)
        mock_book.book_imgs = [Mock(BookImg)]

        mock_book_repository.get_by_id = Mock(return_value=mock_book)

        book_img_id = '1'

        mock_book_img = Mock(BookImg)
        mock_book_img.id = int(book_img_id)
        mock_book_img.id_book = mock_book.id

        mock_book_img_repository.get_by_id = Mock(return_value=mock_book_img)

        book_img_service.delete_book_img(book_id, book_img_id)


def test_update_book_img_from_a_book(
    book_img_service: BookImgService,
    app: Flask,
    mock_book_repository: Mock,
    mock_book_img_repository: Mock,
):
    with app.app_context(), patch(
        'utils.file.uploader.BookImageUploader.delete', new_callable=Mock()
    ) as mock_BookImageUploader_delete:
        book_id = '1'

        mock_book = Mock(Book)
        mock_book.id = int(book_id)

        mock_book_repository.get_by_id = Mock(return_value=mock_book)

        book_img_id = '1'

        book_img = BookImg('http://localhost/books/photos/old_image.jpg')
        book_img.id = int(book_img_id)
        book_img.id_book = mock_book.id

        mock_book_img_repository.get_by_id = Mock(return_value=book_img)

        mock_dto = create_autospec(BookImgInputDTO)
        mock_dto.img = create_autospec(BookImageUploader)
        mock_dto.img.get_url = Mock(return_value='http://localhost/books/photos/new_image.jpg')

        result = book_img_service.update_book_img(book_id, book_img_id, mock_dto)

        mock_dto.img.get_url.assert_called_once()
        mock_dto.img.save.assert_called_once()
        mock_BookImageUploader_delete.assert_called_once_with(
            'http://localhost/books/photos/old_image.jpg'
        )
        mock_book_repository.get_by_id.assert_called_once_with(book_id)
        mock_book_img_repository.get_by_id.assert_called_once_with(book_img_id)
        mock_book_img_repository.update.assert_called_once()

        assert isinstance(result, BookImg)
        assert result.id == book_img.id
        assert result.id_book == book_img.id_book
        assert result.img_url == mock_dto.img.get_url()


def test_when_try_to_update_book_img_from_a_book_doesnt_own_this_image_raises_BookDoesntOwnThisImg(
    book_img_service: BookImgService,
    app: Flask,
    mock_book_repository: Mock,
    mock_book_img_repository: Mock,
):
    with pytest.raises(BookImgException.BookDoesntOwnThisImg), app.app_context():
        book_id = '1'

        mock_book = Mock(Book)
        mock_book.id = int(book_id)

        mock_book_repository.get_by_id = Mock(return_value=mock_book)

        book_img_id = '1'

        mock_book_img = Mock(BookImg)
        mock_book_img.id = int(book_img_id)
        mock_book_img.id_book = 2

        mock_book_img_repository.get_by_id = Mock(return_value=mock_book_img)

        mock_dto = Mock(BookImgInputDTO)

        book_img_service.update_book_img(book_id, book_img_id, mock_dto)
