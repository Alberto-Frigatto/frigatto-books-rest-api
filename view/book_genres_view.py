from flask import Blueprint, Response
from flask_jwt_extended import jwt_required
from flask_restful import Api

from api import BaseResource
from controller import BookGenreController
from dto.input import CreateBookGenreDTO, UpdateBookGenreDTO
from exception.base import ApiException
from response import ResponseError, ResponseSuccess
from schema import book_genres_schema

book_genres_bp = Blueprint('book_genres_bp', __name__)
book_genres_api = Api(book_genres_bp)

controller = BookGenreController()


class BookGenresView(BaseResource):
    def get(self, id: str) -> Response:
        try:
            book_genre = controller.get_book_genre_by_id(id)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = book_genres_schema.dump(book_genre)

            return ResponseSuccess(data).json()

    @jwt_required()
    def delete(self, id: str) -> Response:
        try:
            controller.delete_book_genre(id)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            return ResponseSuccess().json()

    @jwt_required()
    def patch(self, id: str) -> Response:
        try:
            input_dto = UpdateBookGenreDTO()
            updated_book_genre = controller.update_book_genre(id, input_dto)
        except ApiException as e:
            return ResponseError(e).json()
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
            input_dto = CreateBookGenreDTO()
            new_book_genre = controller.create_book_genre(input_dto)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = book_genres_schema.dump(new_book_genre)

            return ResponseSuccess(data, 201).json()


book_genres_api.add_resource(BookGenresView, '/<id>')
book_genres_api.add_resource(BookGenresListView, '')
