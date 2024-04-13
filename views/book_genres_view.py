from flask import Blueprint, Response
from flask_jwt_extended import jwt_required
from flask_restful import Api

from api import BaseResource, api
from controllers import BookGenresController
from handle_errors import CustomError
from response import ResponseError, ResponseSuccess
from schemas import book_genres_schema

book_genres_bp = Blueprint('book_genres_bp', __name__)
book_genres_api = Api(book_genres_bp)

controller = BookGenresController()


class BookGenresView(BaseResource):
    def get(self, id: int) -> Response:
        try:
            book_genre = controller.get_book_genre_by_id(id)
        except CustomError as e:
            return ResponseError(api.errors.get(e.error_name)).json()
        else:
            data = book_genres_schema.dump(book_genre)

            return ResponseSuccess(data).json()

    @jwt_required()
    def delete(self, id: int) -> Response:
        try:
            controller.delete_book_genre(id)
        except CustomError as e:
            return ResponseError(api.errors.get(e.error_name)).json()
        else:
            return ResponseSuccess().json()

    @jwt_required()
    def patch(self, id: int) -> Response:
        try:
            updated_book_genre = controller.update_book_genre(id)
        except CustomError as e:
            return ResponseError(api.errors.get(e.error_name)).json()
        else:
            data = book_genres_schema.dump(updated_book_genre)

            return ResponseSuccess(data).json()


class BookGenresListView(BaseResource):
    def get(self) -> Response:
        book_genres = controller.get_all_book_genres()
        data = book_genres_schema.dump(book_genres, many=True)

        return ResponseSuccess(data).json()

    @jwt_required()
    def post(self) -> Response:
        try:
            new_book_genre = controller.create_book_genre()
        except CustomError as e:
            return ResponseError(api.errors.get(e.error_name)).json()
        else:
            data = book_genres_schema.dump(new_book_genre)

            return ResponseSuccess(data, 201).json()


book_genres_api.add_resource(BookGenresView, '/<int:id>', '/<string:id>')
book_genres_api.add_resource(BookGenresListView, '')
