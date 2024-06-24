from flask import Blueprint, Response
from flask_jwt_extended import jwt_required

from controller import BookController
from dto.input import CreateBookInputDTO, UpdateBookInputDTO
from dto.output import BookOutputDTO
from exception.base import ApiException
from request import Request
from response import ResponseError, ResponseSuccess

book_bp = Blueprint('book_bp', __name__)


class BookView:
    controller = BookController()

    @staticmethod
    @book_bp.get('')
    def get_all_books() -> Response:
        books = BookView.controller.get_all_books()
        data = BookOutputDTO.dump_many(books)

        return ResponseSuccess(data).json()

    @staticmethod
    @book_bp.get('/<id>')
    def get_book_by_id(id: str) -> Response:
        try:
            book = BookView.controller.get_book_by_id(id)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = BookOutputDTO.dump(book)

            return ResponseSuccess(data).json()

    @staticmethod
    @book_bp.post('')
    @jwt_required()
    def create_book() -> Response:
        try:
            request_data = {**Request.get_form(), 'imgs': Request.get_files().getlist('imgs')}
            input_dto = CreateBookInputDTO(**request_data)
            new_book = BookView.controller.create_book(input_dto)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = BookOutputDTO.dump(new_book)

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
            input_book = UpdateBookInputDTO(**Request.get_form())
            updated_book = BookView.controller.update_book(id, input_book)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = BookOutputDTO.dump(updated_book)

            return ResponseSuccess(data).json()
