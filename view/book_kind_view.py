from flask import Blueprint, Response
from flask_jwt_extended import jwt_required

from controller import BookKindController
from dto.input import CreateBookKindDTO, UpdateBookKindDTO
from exception.base import ApiException
from response import ResponseError, ResponseSuccess
from schema import book_kinds_schema

book_kind_bp = Blueprint('book_kind_bp', __name__)


class BookKindView:
    controller = BookKindController()

    @staticmethod
    @book_kind_bp.get('')
    def get_all_book_kinds() -> Response:
        book_kinds = BookKindView.controller.get_all_book_kinds()
        data = book_kinds_schema.dump(book_kinds, many=True)

        return ResponseSuccess(data).json()

    @staticmethod
    @book_kind_bp.get('/<id>')
    def get_book_kind_by_id(id: str) -> Response:
        try:
            book_kind = BookKindView.controller.get_book_kind_by_id(id)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = book_kinds_schema.dump(book_kind)

            return ResponseSuccess(data).json()

    @staticmethod
    @book_kind_bp.post('')
    @jwt_required()
    def create_book_kind() -> Response:
        try:
            input_dto = CreateBookKindDTO()
            new_book_kind = BookKindView.controller.create_book_kind(input_dto)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = book_kinds_schema.dump(new_book_kind)

            return ResponseSuccess(data, 201).json()

    @staticmethod
    @book_kind_bp.delete('/<id>')
    @jwt_required()
    def delete_book_kind(id: str) -> Response:
        try:
            BookKindView.controller.delete_book_kind(id)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            return ResponseSuccess().json()

    @staticmethod
    @book_kind_bp.patch('/<id>')
    @jwt_required()
    def update_book_kind(id: str) -> Response:
        try:
            input_dto = UpdateBookKindDTO()
            updated_book_kind = BookKindView.controller.update_book_kind(id, input_dto)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = book_kinds_schema.dump(updated_book_kind)

            return ResponseSuccess(data).json()
