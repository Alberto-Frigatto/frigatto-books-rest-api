from flask import Blueprint, Response
from flask_restful import Api

from api import BaseResource
from controllers import SearchesController
from handle_errors import CustomError
from response import ResponseError, ResponseSuccess
from schemas import books_schema

searches_bp = Blueprint('searches_bp', __name__)
searches_api = Api(searches_bp)

controller = SearchesController()


class SearchersView(BaseResource):
    def get(self) -> Response:
        try:
            matched_books = controller.search_books()
        except CustomError as e:
            return ResponseError(e).json()
        else:
            data = books_schema.dump(matched_books, many=True)

            return ResponseSuccess(data).json()


searches_api.add_resource(SearchersView, '')
