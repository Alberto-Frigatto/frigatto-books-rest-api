from flask import Blueprint, Response

from controller import ISearchController
from dto.input import SearchInputDTO
from dto.output import BookOutputDTO
from request import Request
from response import PaginationResponse

search_bp = Blueprint('search_bp', __name__)


class SearchView:
    @staticmethod
    @search_bp.get('')
    def search_books(controller: ISearchController) -> Response:
        input_dto = SearchInputDTO(**Request.get_json())
        page = Request.get_int_arg('page', default=1)

        pagination = controller.search_books(page, input_dto)
        data = BookOutputDTO.dump_many(pagination.items)

        return PaginationResponse(data, pagination).json()
