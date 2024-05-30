from flask import Blueprint, Response, send_file
from flask_jwt_extended import jwt_required
from flask_restful import Api

from api import BaseResource
from controller import BookController
from exception.base import ApiException
from response import ResponseError, ResponseSuccess
from schema import books_schema

books_bp = Blueprint('books_bp', __name__)
books_api = Api(books_bp)

controller = BookController()


class BooksView(BaseResource):
    def get(self, id: str) -> Response:
        try:
            book = controller.get_book_by_id(id)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = books_schema.dump(book)

            return ResponseSuccess(data).json()

    @jwt_required()
    def delete(self, id: str) -> Response:
        try:
            controller.delete_book(id)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            return ResponseSuccess().json()

    @jwt_required()
    def patch(self, id: str) -> Response:
        try:
            updated_book = controller.update_book(id)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = books_schema.dump(updated_book)

            return ResponseSuccess(data).json()


class BooksListView(BaseResource):
    def get(self) -> Response:
        books = controller.get_all_books()
        data = books_schema.dump(books, many=True)

        return ResponseSuccess(data).json()

    @jwt_required()
    def post(self) -> Response:
        try:
            new_book = controller.create_book()
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = books_schema.dump(new_book)

            return ResponseSuccess(data, 201).json()


books_api.add_resource(BooksView, '/<id>')
books_api.add_resource(BooksListView, '')
