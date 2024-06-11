from flask import Blueprint, Response
from flask_jwt_extended import jwt_required

from controller import SavedBookController
from exception.base import ApiException
from response import ResponseError, ResponseSuccess
from schema import books_schema

saved_book_bp = Blueprint('saved_book_bp', __name__)


class SavedBookView:
    controller = SavedBookController()

    @staticmethod
    @saved_book_bp.post('/<id>/save')
    @jwt_required()
    def save_book(id: str) -> Response:
        try:
            saved_book = SavedBookView.controller.save_book(id)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = books_schema.dump(saved_book)

            return ResponseSuccess(data, 201).json()

    @staticmethod
    @saved_book_bp.get('/saved')
    @jwt_required()
    def get_all_saved_books() -> Response:
        saved_books = SavedBookView.controller.get_all_saved_books()
        data = books_schema.dump(saved_books, many=True)

        return ResponseSuccess(data).json()

    @staticmethod
    @saved_book_bp.delete('/saved/<id_book>')
    @jwt_required()
    def delete_saved_book(id_book: str) -> Response:
        try:
            SavedBookView.controller.delete_saved_book(id_book)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            return ResponseSuccess().json()
