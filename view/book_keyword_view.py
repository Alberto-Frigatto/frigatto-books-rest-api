from flask import Blueprint, Response
from flask_jwt_extended import jwt_required

from controller import IBookKeywordController
from dto.input import BookKeywordInputDTO
from dto.output import BookKeywordOutputDTO
from request import Request
from response import SuccessResponse

book_keyword_bp = Blueprint('book_keyword_bp', __name__)


class BookKeywordView:
    @staticmethod
    @book_keyword_bp.post('/<id_book>/keywords')
    @jwt_required()
    def create_book_keyword(id_book: str, controller: IBookKeywordController) -> Response:
        input_dto = BookKeywordInputDTO(**Request.get_json())

        new_book_keyword = controller.create_book_keyword(id_book, input_dto)
        data = BookKeywordOutputDTO.dump(new_book_keyword)

        return SuccessResponse(data, 201).json()

    @staticmethod
    @book_keyword_bp.delete('/<id_book>/keywords/<id_keyword>')
    @jwt_required()
    def delete_book_keyword(
        id_book: str, id_keyword: str, controller: IBookKeywordController
    ) -> Response:
        controller.delete_book_keyword(id_book, id_keyword)

        return SuccessResponse().json()
