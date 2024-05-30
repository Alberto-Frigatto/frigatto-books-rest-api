from flask import Blueprint, Response
from flask_jwt_extended import jwt_required
from flask_restful import Api

from api import BaseResource
from controller import BookKindController
from exception.base import ApiException
from response import ResponseError, ResponseSuccess
from schema import book_kinds_schema

book_kinds_bp = Blueprint('book_kinds_bp', __name__)
book_kinds_api = Api(book_kinds_bp)

controller = BookKindController()


class BookKindsView(BaseResource):
    def get(self, id: str) -> Response:
        try:
            book_kind = controller.get_book_kind_by_id(id)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = book_kinds_schema.dump(book_kind)

            return ResponseSuccess(data).json()

    @jwt_required()
    def delete(self, id: str) -> Response:
        try:
            controller.delete_book_kind(id)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            return ResponseSuccess().json()

    @jwt_required()
    def patch(self, id: str) -> Response:
        try:
            updated_book_kind = controller.update_book_kind(id)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = book_kinds_schema.dump(updated_book_kind)

            return ResponseSuccess(data).json()


class BookKindsListView(BaseResource):
    def get(self) -> Response:
        book_kinds = controller.get_all_book_kinds()
        data = book_kinds_schema.dump(book_kinds, many=True)

        return ResponseSuccess(data).json()

    @jwt_required()
    def post(self) -> Response:
        try:
            new_book_kind = controller.create_book_kind()
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = book_kinds_schema.dump(new_book_kind)

            return ResponseSuccess(data, 201).json()


book_kinds_api.add_resource(BookKindsView, '/<id>')
book_kinds_api.add_resource(BookKindsListView, '')
