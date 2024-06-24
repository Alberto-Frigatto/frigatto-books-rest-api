from flask import Blueprint, Response

from controller import SearchController
from dto.input import SearchInputDTO
from dto.output import BookOutputDTO
from exception.base import ApiException
from request import Request
from response import ResponseError, ResponseSuccess

search_bp = Blueprint('search_bp', __name__)

controller = SearchController()


class SearchView:
    @staticmethod
    @search_bp.get('')
    def search_books() -> Response:
        try:
            input_dto = SearchInputDTO(**Request.get_json())
            matched_books = controller.search_books(input_dto)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = BookOutputDTO.dump_many(matched_books)

            return ResponseSuccess(data).json()
