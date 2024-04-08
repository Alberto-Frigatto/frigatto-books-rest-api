from flask import Blueprint, Response
from flask_restful import Api, Resource

from api import api
from controllers import BookKindsController
from handle_errors import CustomError
from response import ResponseError, ResponseSuccess
from schemas import book_kinds_schema

book_kinds_bp = Blueprint('book_kinds_bp', __name__)
book_kinds_api = Api(book_kinds_bp)

controller = BookKindsController()


class BookKindsView(Resource):
    def get(self, id: int) -> Response:
        try:
            book_kind = controller.get_book_kind(id)
        except CustomError as e:
            return ResponseError(api.errors.get(e.error_name)).json()
        else:
            data = book_kinds_schema.dump(book_kind)

            return ResponseSuccess(data).json()

    def options(self, id: int) -> Response:
        return ResponseSuccess().json()


class BookKindsListView(Resource):
    def get(self) -> Response:
        book_kinds = controller.get_all_book_kinds()
        data = book_kinds_schema.dump(book_kinds, many=True)

        return ResponseSuccess(data).json()

    def post(self) -> Response:
        try:
            new_book_kind = controller.create_book_kind()
        except CustomError as e:
            return ResponseError(api.errors.get(e.error_name)).json()
        else:
            data = book_kinds_schema.dump(new_book_kind)

            return ResponseSuccess(data, 201).json()

    def options(self) -> Response:
        return ResponseSuccess().json()


book_kinds_api.add_resource(BookKindsListView, '')
book_kinds_api.add_resource(BookKindsView, '/<int:id>', '/<string:id>')
