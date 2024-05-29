from flask import Blueprint, Response
from flask_restful import Api

from api import BaseResource
from controller import SearchController
from handle_errors import CustomError
from response import ResponseError, ResponseSuccess
from schema import books_schema

searches_bp = Blueprint('searches_bp', __name__)
searches_api = Api(searches_bp)

controller = SearchController()


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
