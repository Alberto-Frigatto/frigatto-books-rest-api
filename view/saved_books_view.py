from flask import Blueprint, Response
from flask_jwt_extended import jwt_required
from flask_restful import Api

from api import BaseResource
from controller import SavedBooksController
from handle_errors import CustomError
from response import ResponseError, ResponseSuccess
from schema import books_schema

saved_books_bp = Blueprint('saved_books_bp', __name__)
saved_books_api = Api(saved_books_bp)

controller = SavedBooksController()


class SavedBooksView(BaseResource):
    @jwt_required()
    def post(self, id: str) -> Response:
        try:
            saved_book = controller.save_book(id)
        except CustomError as e:
            return ResponseError(e).json()
        else:
            data = books_schema.dump(saved_book)

            return ResponseSuccess(data, 201).json()


class SavedBooksListView(BaseResource):
    @jwt_required()
    def get(self) -> Response:
        saved_books = controller.get_all_saved_books()
        data = books_schema.dump(saved_books, many=True)

        return ResponseSuccess(data).json()


class DeleteSavedBooksView(BaseResource):
    @jwt_required()
    def delete(self, id_book: str) -> Response:
        try:
            controller.delete_saved_book(id_book)
        except CustomError as e:
            return ResponseError(e).json()
        else:
            return ResponseSuccess().json()


saved_books_api.add_resource(SavedBooksView, '/<id>/save')
saved_books_api.add_resource(SavedBooksListView, '/saved')
saved_books_api.add_resource(DeleteSavedBooksView, '/saved/<id_book>')
