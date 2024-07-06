from flask import Blueprint, Response
from flask_jwt_extended import jwt_required

from controller import IBookGenreController
from dto.input import BookGenreInputDTO
from dto.output import BookGenreOutputDTO
from utils.request import Request
from utils.response import CreatedResponse, NoContentResponse, OkResponse, PaginationResponse

book_genre_bp = Blueprint('book_genre_bp', __name__)


class BookGenreView:
    @staticmethod
    @book_genre_bp.get('')
    def get_all_book_genres(controller: IBookGenreController) -> Response:
        page = Request.get_int_arg('page', default=1)
        pagination = controller.get_all_book_genres(page)
        data = BookGenreOutputDTO.dump_many(pagination.items)

        return PaginationResponse(data, pagination).json()

    @staticmethod
    @book_genre_bp.get('/<id>')
    def get_book_genre_by_id(id: str, controller: IBookGenreController) -> Response:
        book_genre = controller.get_book_genre_by_id(id)
        data = BookGenreOutputDTO.dump(book_genre)

        return OkResponse(data).json()

    @staticmethod
    @book_genre_bp.post('')
    @jwt_required()
    def create_book_genre(controller: IBookGenreController) -> Response:
        input_dto = BookGenreInputDTO(**Request.get_json())
        new_book_genre = controller.create_book_genre(input_dto)
        data = BookGenreOutputDTO.dump(new_book_genre)

        return CreatedResponse(data).json()

    @staticmethod
    @book_genre_bp.delete('/<id>')
    @jwt_required()
    def delete_book_genre(id: str, controller: IBookGenreController) -> Response:
        controller.delete_book_genre(id)
        return NoContentResponse().json()

    @staticmethod
    @book_genre_bp.patch('/<id>')
    @jwt_required()
    def update_book_genre(id: str, controller: IBookGenreController) -> Response:
        input_dto = BookGenreInputDTO(**Request.get_json())
        updated_book_genre = controller.update_book_genre(id, input_dto)
        data = BookGenreOutputDTO.dump(updated_book_genre)

        return OkResponse(data).json()
