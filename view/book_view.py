from flask import Blueprint, Response
from flask_jwt_extended import jwt_required
from werkzeug.datastructures import FileStorage

from controller import IBookController
from dto.input import CreateBookInputDTO, UpdateBookInputDTO
from dto.output import BookOutputDTO
from utils.request import Request
from utils.response import PaginationResponse, SuccessResponse

book_bp = Blueprint('book_bp', __name__)


class BookView:
    @staticmethod
    @book_bp.get('')
    def get_all_books(controller: IBookController) -> Response:
        page = Request.get_int_arg('page', default=1)
        paginate = controller.get_all_books(page)
        data = BookOutputDTO.dump_many(paginate.items)

        return PaginationResponse(data, paginate).json()

    @staticmethod
    @book_bp.get('/<id>')
    def get_book_by_id(id: str, controller: IBookController) -> Response:
        book = controller.get_book_by_id(id)
        data = BookOutputDTO.dump(book)

        return SuccessResponse(data).json()

    @staticmethod
    @book_bp.post('')
    @jwt_required()
    def create_book(controller: IBookController) -> Response:
        request_data: dict[str, str | list[FileStorage]] = {**Request.get_form()}

        if 'imgs' not in request_data:
            request_data['imgs'] = Request.get_files().getlist('imgs')

        input_dto = CreateBookInputDTO(**request_data)

        new_book = controller.create_book(input_dto)
        data = BookOutputDTO.dump(new_book)

        return SuccessResponse(data, 201).json()

    @staticmethod
    @book_bp.delete('/<id>')
    @jwt_required()
    def delete_book(id: str, controller: IBookController) -> Response:
        controller.delete_book(id)

        return SuccessResponse().json()

    @staticmethod
    @book_bp.patch('/<id>')
    @jwt_required()
    def update_book(id: str, controller: IBookController) -> Response:
        input_book = UpdateBookInputDTO(**Request.get_form())

        updated_book = controller.update_book(id, input_book)
        data = BookOutputDTO.dump(updated_book)

        return SuccessResponse(data).json()
