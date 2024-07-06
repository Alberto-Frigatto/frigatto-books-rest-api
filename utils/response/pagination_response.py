from typing import Any

import flask
from flask import request, url_for
from flask_sqlalchemy.pagination import Pagination

from .base import Response


class PaginationResponse(Response):
    def __init__(self, data: list[dict[str, Any]], pagination_details: Pagination) -> None:
        self._pagination_details = pagination_details
        self._data = data

    def json(self) -> flask.Response:
        total_items = self._pagination_details.total or 0
        actual_page = self._pagination_details.page or 1
        prev_page = (
            url_for(request.endpoint, page=self._pagination_details.prev_num)
            if self._pagination_details.has_prev and request.endpoint
            else None
        )
        next_page = (
            url_for(request.endpoint, page=self._pagination_details.next_num)
            if self._pagination_details.has_next and request.endpoint
            else None
        )

        response = {
            'data': self._data,
            'total_items': total_items,
            'total_pages': self._pagination_details.pages,
            'page': actual_page,
            'per_page': self._pagination_details.per_page,
            'has_prev': self._pagination_details.has_prev,
            'has_next': self._pagination_details.has_next,
            'prev_page': prev_page,
            'next_page': next_page,
        }

        return super()._make_response(payload=response, status=200)
