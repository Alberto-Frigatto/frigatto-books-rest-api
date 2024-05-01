from flask import Blueprint, Response
from flask_jwt_extended import jwt_required
from flask_restful import Api

from api import BaseResource
from controllers import BookKeywordsController
from handle_errors import CustomError
from response import ResponseError, ResponseSuccess
from schemas import book_keywords_schema

book_keywords_bp = Blueprint('book_keywords_bp', __name__)
book_keywords_api = Api(book_keywords_bp)

controller = BookKeywordsController()


class AddBookKeywordsView(BaseResource):
    @jwt_required()
    def post(self, id_book: int) -> Response:
        try:
            new_book_keyword = controller.create_book_keyword(id_book)
        except CustomError as e:
            return ResponseError(e).json()
        else:
            data = book_keywords_schema.dump(new_book_keyword)

            return ResponseSuccess(data, 201).json()


class DeleteBookKeywordsView(BaseResource):
    @jwt_required()
    def delete(self, id_book: int, id_keyword: int) -> Response:
        try:
            controller.delete_book_keyword(id_book, id_keyword)
        except CustomError as e:
            return ResponseError(e).json()
        else:
            return ResponseSuccess().json()


book_keywords_api.add_resource(
    AddBookKeywordsView,
    '/<int:id_book>/keywords',
    '/<string:id_book>/keywords',
)
book_keywords_api.add_resource(
    DeleteBookKeywordsView,
    '/<int:id_book>/keywords/<int:id_keyword>',
    '/<string:id_book>/keywords/<string:id_keyword>',
)
