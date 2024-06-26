from flask import Blueprint, Response
from flask_jwt_extended import jwt_required

from controller import IBookKindController
from dto.input import BookKindInputDTO
from dto.output import BookKindOutputDTO
from request import Request
from response import ResponseSuccess

book_kind_bp = Blueprint('book_kind_bp', __name__)


class BookKindView:
    @staticmethod
    @book_kind_bp.get('')
    def get_all_book_kinds(controller: IBookKindController) -> Response:
        book_kinds = controller.get_all_book_kinds()
        data = BookKindOutputDTO.dump_many(book_kinds)

        return ResponseSuccess(data).json()

    @staticmethod
    @book_kind_bp.get('/<id>')
    def get_book_kind_by_id(id: str, controller: IBookKindController) -> Response:
        book_kind = controller.get_book_kind_by_id(id)
        data = BookKindOutputDTO.dump(book_kind)

        return ResponseSuccess(data).json()

    @staticmethod
    @book_kind_bp.post('')
    @jwt_required()
    def create_book_kind(controller: IBookKindController) -> Response:
        input_dto = BookKindInputDTO(**Request.get_json())

        new_book_kind = controller.create_book_kind(input_dto)
        data = BookKindOutputDTO.dump(new_book_kind)

        return ResponseSuccess(data, 201).json()

    @staticmethod
    @book_kind_bp.delete('/<id>')
    @jwt_required()
    def delete_book_kind(id: str, controller: IBookKindController) -> Response:
        controller.delete_book_kind(id)

        return ResponseSuccess().json()

    @staticmethod
    @book_kind_bp.patch('/<id>')
    @jwt_required()
    def update_book_kind(id: str, controller: IBookKindController) -> Response:
        input_dto = BookKindInputDTO(**Request.get_json())

        updated_book_kind = controller.update_book_kind(id, input_dto)
        data = BookKindOutputDTO.dump(updated_book_kind)

        return ResponseSuccess(data).json()
