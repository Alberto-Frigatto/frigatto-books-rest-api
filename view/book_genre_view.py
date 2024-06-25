from flask import Blueprint, Response
from flask_jwt_extended import jwt_required

from controller import BookGenreController
from dto.input import BookGenreInputDTO
from dto.output import BookGenreOutputDTO
from request import Request
from response import ResponseSuccess

book_genre_bp = Blueprint('book_genre_bp', __name__)


class BookGenreView:
    @staticmethod
    @book_genre_bp.get('')
    def get_all_book_genres(controller: BookGenreController) -> Response:
        book_genres = controller.get_all_book_genres()
        data = BookGenreOutputDTO.dump_many(book_genres)

        return ResponseSuccess(data).json()

    @staticmethod
    @book_genre_bp.get('/<id>')
    def get_book_genre_by_id(id: str, controller: BookGenreController) -> Response:
        book_genre = controller.get_book_genre_by_id(id)
        data = BookGenreOutputDTO.dump(book_genre)

        return ResponseSuccess(data).json()

    @staticmethod
    @book_genre_bp.post('')
    @jwt_required()
    def create_book_genre(controller: BookGenreController) -> Response:
        input_dto = BookGenreInputDTO(**Request.get_json())
        new_book_genre = controller.create_book_genre(input_dto)
        data = BookGenreOutputDTO.dump(new_book_genre)

        return ResponseSuccess(data, 201).json()

    @staticmethod
    @book_genre_bp.delete('/<id>')
    @jwt_required()
    def delete_book_genre(id: str, controller: BookGenreController) -> Response:
        controller.delete_book_genre(id)
        return ResponseSuccess().json()

    @staticmethod
    @book_genre_bp.patch('/<id>')
    @jwt_required()
    def update_book_genre(id: str, controller: BookGenreController) -> Response:
        input_dto = BookGenreInputDTO(**Request.get_json())
        updated_book_genre = controller.update_book_genre(id, input_dto)
        data = BookGenreOutputDTO.dump(updated_book_genre)

        return ResponseSuccess(data).json()
