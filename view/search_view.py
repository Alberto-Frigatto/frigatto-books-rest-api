from flask import Blueprint, Response

from controller import SearchController
from dto.input import SearchDTO
from exception.base import ApiException
from response import ResponseError, ResponseSuccess
from schema import books_schema

search_bp = Blueprint('search_bp', __name__)

controller = SearchController()


class SearchView:
    @staticmethod
    @search_bp.get('')
    def search_books() -> Response:
        try:
            input_dto = SearchDTO()
            matched_books = controller.search_books(input_dto)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = books_schema.dump(matched_books, many=True)

            return ResponseSuccess(data).json()
