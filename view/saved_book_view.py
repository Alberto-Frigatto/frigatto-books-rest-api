from flask import Blueprint, Response
from flask_jwt_extended import jwt_required

from controller import ISavedBookController
from dto.output import BookOutputDTO
from response import ResponseSuccess

saved_book_bp = Blueprint('saved_book_bp', __name__)


class SavedBookView:
    @staticmethod
    @saved_book_bp.post('/<id>/save')
    @jwt_required()
    def save_book(id: str, controller: ISavedBookController) -> Response:
        saved_book = controller.save_book(id)
        data = BookOutputDTO.dump(saved_book)

        return ResponseSuccess(data, 201).json()

    @staticmethod
    @saved_book_bp.get('/saved')
    @jwt_required()
    def get_all_saved_books(controller: ISavedBookController) -> Response:
        saved_books = controller.get_all_saved_books()
        data = BookOutputDTO.dump_many(saved_books)

        return ResponseSuccess(data).json()

    @staticmethod
    @saved_book_bp.delete('/saved/<id_book>')
    @jwt_required()
    def delete_saved_book(id_book: str, controller: ISavedBookController) -> Response:
        controller.delete_saved_book(id_book)

        return ResponseSuccess().json()
