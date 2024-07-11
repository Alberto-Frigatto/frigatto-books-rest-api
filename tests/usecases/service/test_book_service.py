from decimal import Decimal
from unittest.mock import Mock, create_autospec

import pytest
from flask import Flask
from flask_sqlalchemy.pagination import Pagination

from app import create_app
from dto.input import CreateBookInputDTO, UpdateBookInputDTO
from model import Book, BookGenre, BookImg, BookKeyword, BookKind
from repository import IBookGenreRepository, IBookKindRepository, IBookRepository
from service.impl import BookService
from utils.file.uploader import BookImageUploader


@pytest.fixture
def app() -> Flask:
    return create_app(True)


@pytest.fixture
def mock_book_repository() -> Mock:
    return create_autospec(IBookRepository)


@pytest.fixture
def mock_book_genre_repository() -> Mock:
    return create_autospec(IBookGenreRepository)


@pytest.fixture
def mock_book_kind_repository() -> Mock:
    return create_autospec(IBookKindRepository)


@pytest.fixture
def book_service(
    mock_book_repository: Mock,
    mock_book_genre_repository: Mock,
    mock_book_kind_repository: Mock,
) -> BookService:
    return BookService(mock_book_repository, mock_book_genre_repository, mock_book_kind_repository)


def test_get_all_books(book_service: BookService, app: Flask, mock_book_repository: Mock):
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

        mock_book_repository.get_all = Mock(return_value=mock_pagination)

        page = 1
        result = book_service.get_all_books(page)

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

        mock_book_repository.get_all.assert_called_once_with(page)


def test_get_book_by_id(book_service: BookService, app: Flask, mock_book_repository: Mock):
    with app.app_context():
        book_id = '1'

        mock_book = Mock(Book)

        mock_book_repository.get_by_id = Mock(return_value=mock_book)

        result = book_service.get_book_by_id(book_id)

        assert isinstance(result, Book)
        assert result == mock_book

        mock_book_repository.get_by_id.assert_called_once_with(book_id)


def test_create_book(
    book_service: BookService,
    app: Flask,
    mock_book_repository: Mock,
    mock_book_genre_repository: Mock,
    mock_book_kind_repository: Mock,
):
    with app.app_context():
        mock_dto = create_autospec(CreateBookInputDTO)
        mock_dto.name = Mock()
        mock_dto.price = Mock()
        mock_dto.author = Mock()
        mock_dto.release_year = Mock()
        mock_dto.id_book_kind = Mock()
        mock_dto.id_book_genre = Mock()
        mock_dto.keywords = [Mock() for _ in range(5)]
        mock_dto.imgs = [create_autospec(BookImageUploader) for _ in range(3)]

        mock_book_kind = Mock(BookKind)
        mock_book_kind_repository.get_by_id = Mock(return_value=mock_book_kind)
        mock_book_genre = Mock(BookGenre)
        mock_book_genre_repository.get_by_id = Mock(return_value=mock_book_genre)

        result = book_service.create_book(mock_dto)

        for img in mock_dto.imgs:
            img.save.assert_called_once()
            img.get_url.assert_called_once()

        mock_book_kind_repository.get_by_id.assert_called_once_with(str(mock_dto.id_book_kind))
        mock_book_genre_repository.get_by_id.assert_called_once_with(str(mock_dto.id_book_genre))
        mock_book_repository.add.assert_called_once_with(result)

        assert isinstance(result, Book)
        assert result.name == mock_dto.name
        assert result.price == mock_dto.price
        assert result.author == mock_dto.author
        assert result.release_year == mock_dto.release_year
        assert result.book_kind == mock_book_kind
        assert result.book_genre == mock_book_genre
        assert all(isinstance(keyword, BookKeyword) for keyword in result.book_keywords)
        assert all(isinstance(img, BookImg) for img in result.book_imgs)


def test_delete_book(book_service: BookService, app: Flask, mock_book_repository: Mock):
    with app.app_context():
        book_id = '1'

        result = book_service.delete_book(book_id)

        assert result is None

        mock_book_repository.delete.assert_called_once_with(book_id)


def test_update_book_name(book_service: BookService, app: Flask, mock_book_repository: Mock):
    with app.app_context():
        book_id = '1'

        book = Book(Mock(), Mock(), Mock(), Mock())
        book.book_genre = Mock()
        book.book_kind = Mock()
        book.book_imgs = [BookImg(Mock()) for _ in range(3)]
        book.book_keywords = [BookKeyword(Mock()) for _ in range(3)]

        mock_book_repository.get_by_id = Mock(return_value=book)

        mock_dto = create_autospec(UpdateBookInputDTO)
        mock_dto.name = 'novo nome'
        mock_dto.items = {
            'name': mock_dto.name,
            'price': None,
            'author': None,
            'release_year': None,
            'id_book_kind': None,
            'id_book_genre': None,
        }.items()

        result = book_service.update_book(book_id, mock_dto)

        assert isinstance(result, Book)
        assert result.name == mock_dto.name
        assert result.price == book.price
        assert result.author == book.author
        assert result.release_year == book.release_year
        assert result.book_kind == book.book_kind
        assert result.book_genre == book.book_genre
        assert result.book_imgs == book.book_imgs
        assert result.book_keywords == book.book_keywords

        mock_book_repository.get_by_id.assert_called_once_with(book_id)
        mock_book_repository.update.assert_called_once_with(result)


def test_update_book_price(book_service: BookService, app: Flask, mock_book_repository: Mock):
    with app.app_context():
        book_id = '1'

        book = Book(Mock(), Mock(), Mock(), Mock())
        book.book_genre = Mock()
        book.book_kind = Mock()
        book.book_imgs = [BookImg(Mock()) for _ in range(3)]
        book.book_keywords = [BookKeyword(Mock()) for _ in range(3)]

        mock_book_repository.get_by_id = Mock(return_value=book)

        mock_dto = create_autospec(UpdateBookInputDTO)
        mock_dto.price = Decimal('50')
        mock_dto.items = {
            'name': None,
            'price': mock_dto.price,
            'author': None,
            'release_year': None,
            'id_book_kind': None,
            'id_book_genre': None,
        }.items()

        result = book_service.update_book(book_id, mock_dto)

        assert isinstance(result, Book)
        assert result.name == book.name
        assert result.price == mock_dto.price
        assert result.author == book.author
        assert result.release_year == book.release_year
        assert result.book_kind == book.book_kind
        assert result.book_genre == book.book_genre
        assert result.book_imgs == book.book_imgs
        assert result.book_keywords == book.book_keywords

        mock_book_repository.get_by_id.assert_called_once_with(book_id)
        mock_book_repository.update.assert_called_once_with(result)


def test_update_book_author(book_service: BookService, app: Flask, mock_book_repository: Mock):
    with app.app_context():
        book_id = '1'

        book = Book(Mock(), Mock(), Mock(), Mock())
        book.book_genre = Mock()
        book.book_kind = Mock()
        book.book_imgs = [BookImg(Mock()) for _ in range(3)]
        book.book_keywords = [BookKeyword(Mock()) for _ in range(3)]

        mock_book_repository.get_by_id = Mock(return_value=book)

        mock_dto = create_autospec(UpdateBookInputDTO)
        mock_dto.author = 'Novo Autor'
        mock_dto.items = {
            'name': None,
            'price': None,
            'author': mock_dto.author,
            'release_year': None,
            'id_book_kind': None,
            'id_book_genre': None,
        }.items()

        result = book_service.update_book(book_id, mock_dto)

        assert isinstance(result, Book)
        assert result.name == book.name
        assert result.price == book.price
        assert result.author == mock_dto.author
        assert result.release_year == book.release_year
        assert result.book_kind == book.book_kind
        assert result.book_genre == book.book_genre
        assert result.book_imgs == book.book_imgs
        assert result.book_keywords == book.book_keywords

        mock_book_repository.get_by_id.assert_called_once_with(book_id)
        mock_book_repository.update.assert_called_once_with(result)


def test_update_book_release_year(
    book_service: BookService, app: Flask, mock_book_repository: Mock
):
    with app.app_context():
        book_id = '1'

        book = Book(Mock(), Mock(), Mock(), Mock())
        book.book_genre = Mock()
        book.book_kind = Mock()
        book.book_imgs = [BookImg(Mock()) for _ in range(3)]
        book.book_keywords = [BookKeyword(Mock()) for _ in range(3)]

        mock_book_repository.get_by_id = Mock(return_value=book)

        mock_dto = create_autospec(UpdateBookInputDTO)
        mock_dto.release_year = 2000
        mock_dto.items = {
            'name': None,
            'price': None,
            'author': None,
            'release_year': mock_dto.release_year,
            'id_book_kind': None,
            'id_book_genre': None,
        }.items()

        result = book_service.update_book(book_id, mock_dto)

        assert isinstance(result, Book)
        assert result.name == book.name
        assert result.price == book.price
        assert result.author == book.author
        assert result.release_year == mock_dto.release_year
        assert result.book_kind == book.book_kind
        assert result.book_genre == book.book_genre
        assert result.book_imgs == book.book_imgs
        assert result.book_keywords == book.book_keywords

        mock_book_repository.get_by_id.assert_called_once_with(book_id)
        mock_book_repository.update.assert_called_once_with(result)


def test_update_book_book_kind(
    book_service: BookService,
    app: Flask,
    mock_book_repository: Mock,
    mock_book_kind_repository: Mock,
):
    with app.app_context():
        book_id = '1'

        book = Book(Mock(), Mock(), Mock(), Mock())
        book.book_genre = Mock()
        book.book_kind = Mock()
        book.book_imgs = [BookImg(Mock()) for _ in range(3)]
        book.book_keywords = [BookKeyword(Mock()) for _ in range(3)]

        mock_book_repository.get_by_id = Mock(return_value=book)

        mock_dto = create_autospec(UpdateBookInputDTO)
        mock_dto.id_book_kind = '2'
        mock_dto.items = {
            'name': None,
            'price': None,
            'author': None,
            'release_year': None,
            'id_book_kind': mock_dto.id_book_kind,
            'id_book_genre': None,
        }.items()

        mock_book_kind = Mock(BookKind)
        mock_book_kind_repository.get_by_id = Mock(return_value=mock_book_kind)

        result = book_service.update_book(book_id, mock_dto)

        assert isinstance(result, Book)
        assert result.name == book.name
        assert result.price == book.price
        assert result.author == book.author
        assert result.release_year == book.release_year
        assert result.book_kind == mock_book_kind
        assert result.book_genre == book.book_genre
        assert result.book_imgs == book.book_imgs
        assert result.book_keywords == book.book_keywords

        mock_book_kind_repository.get_by_id.assert_called_once_with(mock_dto.id_book_kind)
        mock_book_repository.get_by_id.assert_called_once_with(book_id)
        mock_book_repository.update.assert_called_once_with(result)


def test_update_book_book_genre(
    book_service: BookService,
    app: Flask,
    mock_book_repository: Mock,
    mock_book_genre_repository: Mock,
):
    with app.app_context():
        book_id = '1'

        book = Book(Mock(), Mock(), Mock(), Mock())
        book.book_genre = Mock()
        book.book_kind = Mock()
        book.book_imgs = [BookImg(Mock()) for _ in range(3)]
        book.book_keywords = [BookKeyword(Mock()) for _ in range(3)]

        mock_book_repository.get_by_id = Mock(return_value=book)

        mock_dto = create_autospec(UpdateBookInputDTO)
        mock_dto.id_book_genre = '2'
        mock_dto.items = {
            'name': None,
            'price': None,
            'author': None,
            'release_year': None,
            'id_book_kind': None,
            'id_book_genre': mock_dto.id_book_genre,
        }.items()

        mock_book_genre = Mock(BookGenre)
        mock_book_genre_repository.get_by_id = Mock(return_value=mock_book_genre)

        result = book_service.update_book(book_id, mock_dto)

        assert isinstance(result, Book)
        assert result.name == book.name
        assert result.price == book.price
        assert result.author == book.author
        assert result.release_year == book.release_year
        assert result.book_kind == book.book_kind
        assert result.book_genre == mock_book_genre
        assert result.book_imgs == book.book_imgs
        assert result.book_keywords == book.book_keywords

        mock_book_genre_repository.get_by_id.assert_called_once_with(mock_dto.id_book_genre)
        mock_book_repository.get_by_id.assert_called_once_with(book_id)
        mock_book_repository.update.assert_called_once_with(result)
