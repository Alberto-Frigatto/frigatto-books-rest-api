from flask import Blueprint, Response
from flask_jwt_extended import jwt_required

from controller import BookController
from dto.input import CreateBookDTO, UpdateBookDTO
from exception.base import ApiException
from response import ResponseError, ResponseSuccess
from schema import books_schema

book_bp = Blueprint('book_bp', __name__)


class BookView:
    controller = BookController()

    @staticmethod
    @book_bp.get('')
    def get_all_books() -> Response:
        books = BookView.controller.get_all_books()
        data = books_schema.dump(books, many=True)

        return ResponseSuccess(data).json()

    @staticmethod
    @book_bp.get('/<id>')
    def get_book_by_id(id: str) -> Response:
        try:
            book = BookView.controller.get_book_by_id(id)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = books_schema.dump(book)

            return ResponseSuccess(data).json()

    @staticmethod
    @book_bp.post('')
    @jwt_required()
    def create_book() -> Response:
        try:
            input_dto = CreateBookDTO()
            new_book = BookView.controller.create_book(input_dto)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = books_schema.dump(new_book)

            return ResponseSuccess(data, 201).json()

    @staticmethod
    @book_bp.delete('/<id>')
    @jwt_required()
    def delete_book(id: str) -> Response:
        try:
            BookView.controller.delete_book(id)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            return ResponseSuccess().json()

    @staticmethod
    @book_bp.patch('/<id>')
    @jwt_required()
    def update_book(id: str) -> Response:
        try:
            input_book = UpdateBookDTO()
            updated_book = BookView.controller.update_book(id, input_book)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = books_schema.dump(updated_book)

            return ResponseSuccess(data).json()
