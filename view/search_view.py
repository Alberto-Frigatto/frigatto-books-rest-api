from flask import Blueprint, Response

from controller import SearchController
from dto.input import SearchInputDTO
from dto.output import BookOutputDTO
from request import Request
from response import ResponseSuccess

search_bp = Blueprint('search_bp', __name__)


class SearchView:
    @staticmethod
    @search_bp.get('')
    def search_books(controller: SearchController) -> Response:
        input_dto = SearchInputDTO(**Request.get_json())

        matched_books = controller.search_books(input_dto)
        data = BookOutputDTO.dump_many(matched_books)

        return ResponseSuccess(data).json()
