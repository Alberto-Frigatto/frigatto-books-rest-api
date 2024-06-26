from flask import Blueprint, Response
from flask_jwt_extended import jwt_required

from controller import IBookController
from dto.input import CreateBookInputDTO, UpdateBookInputDTO
from dto.output import BookOutputDTO
from request import Request
from response import ResponseSuccess

book_bp = Blueprint('book_bp', __name__)


class BookView:
    @staticmethod
    @book_bp.get('')
    def get_all_books(controller: IBookController) -> Response:
        books = controller.get_all_books()
        data = BookOutputDTO.dump_many(books)

        return ResponseSuccess(data).json()

    @staticmethod
    @book_bp.get('/<id>')
    def get_book_by_id(id: str, controller: IBookController) -> Response:
        book = controller.get_book_by_id(id)
        data = BookOutputDTO.dump(book)

        return ResponseSuccess(data).json()

    @staticmethod
    @book_bp.post('')
    @jwt_required()
    def create_book(controller: IBookController) -> Response:
        request_data = {**Request.get_form(), 'imgs': Request.get_files().getlist('imgs')}
        input_dto = CreateBookInputDTO(**request_data)

        new_book = controller.create_book(input_dto)
        data = BookOutputDTO.dump(new_book)

        return ResponseSuccess(data, 201).json()

    @staticmethod
    @book_bp.delete('/<id>')
    @jwt_required()
    def delete_book(id: str, controller: IBookController) -> Response:
        controller.delete_book(id)

        return ResponseSuccess().json()

    @staticmethod
    @book_bp.patch('/<id>')
    @jwt_required()
    def update_book(id: str, controller: IBookController) -> Response:
        input_book = UpdateBookInputDTO(**Request.get_form())

        updated_book = controller.update_book(id, input_book)
        data = BookOutputDTO.dump(updated_book)

        return ResponseSuccess(data).json()
