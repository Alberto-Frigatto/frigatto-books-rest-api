from flask import Blueprint, Response
from flask_jwt_extended import jwt_required

from controller import BookKeywordController
from dto.input import BookKeywordInputDTO
from dto.output import BookKeywordOutputDTO
from exception.base import ApiException
from request import Request
from response import ResponseError, ResponseSuccess

book_keyword_bp = Blueprint('book_keyword_bp', __name__)


class BookKeywordView:
    controller = BookKeywordController()

    @staticmethod
    @book_keyword_bp.post('/<id_book>/keywords')
    @jwt_required()
    def create_book_keyword(id_book: str) -> Response:
        try:
            input_dto = BookKeywordInputDTO(**Request.get_json())
            new_book_keyword = BookKeywordView.controller.create_book_keyword(id_book, input_dto)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = BookKeywordOutputDTO.dump(new_book_keyword)

            return ResponseSuccess(data, 201).json()

    @staticmethod
    @book_keyword_bp.delete('/<id_book>/keywords/<id_keyword>')
    @jwt_required()
    def delete_book_keyword(id_book: str, id_keyword: str) -> Response:
        try:
            BookKeywordView.controller.delete_book_keyword(id_book, id_keyword)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            return ResponseSuccess().json()
