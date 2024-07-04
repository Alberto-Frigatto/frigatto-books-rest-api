from typing import Any

import flask
from flask_sqlalchemy.pagination import Pagination

from .base import Response


class PaginationResponse(Response):
    def __init__(self, data: list[dict[str, Any]], pagination_details: Pagination) -> None:
        self._pagination_details = pagination_details
        self._data = data

    def json(self) -> flask.Response:
        status = 200
        total_items = (
            self._pagination_details.total if self._pagination_details.total is not None else 0
        )

        response = {
            'error': False,
            'status': status,
            'data': self._data,
            'total_items': total_items,
            'total_pages': self._pagination_details.pages,
            'page': self._pagination_details.page,
            'per_page': self._pagination_details.per_page,
            'has_prev': self._pagination_details.has_prev,
            'has_next': self._pagination_details.has_next,
            'prev_page': self._pagination_details.prev_num,
            'next_page': self._pagination_details.next_num,
        }

        return super()._make_response(response, status)
