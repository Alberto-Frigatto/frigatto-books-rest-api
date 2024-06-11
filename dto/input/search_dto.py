from typing import Any

from dto.base import InputDTO
from dto.constraints import NumberConstraints
from exception import GeneralException


class SearchDTO(InputDTO):
    query: str | None = None
    filter: dict = {
        'id_kind': None,
        'id_genre': None,
        'release_year': None,
        'price': {
            'min': None,
            'max': None,
        },
    }

    def __init__(self) -> None:
        data = super()._get_json_data()
        self._validate_data(data)
        self._set_fields(data)

    def _validate_data(self, data: dict) -> None:
        query = data.get('query')
        filter = data.get('filter')

        if not all(
            (
                self._are_request_fields_valid(data),
                self._is_filter_valid(filter),
                self._is_query_valid(query),
            )
        ):
            raise GeneralException.InvalidDataSent()

    def _are_request_fields_valid(self, data: dict) -> bool:
        fields = self.__annotations__.keys()

        return all(field in fields for field in data)

    def _is_query_valid(self, query: Any) -> bool:
        return query is None or isinstance(query, str)

    def _is_filter_valid(self, filter: Any) -> bool:
        return filter is None or (
            isinstance(filter, dict)
            and self._does_filter_has_any_parameter(filter)
            and self._is_id_kind_valid(filter.get('id_kind'))
            and self._is_id_genre_valid(filter.get('id_genre'))
            and self._is_release_year_valid(filter.get('release_year'))
            and self._is_price_valid(filter.get('price'))
        )

    def _does_filter_has_any_parameter(self, filter: dict) -> bool:
        return any(key in filter for key in self.filter.keys())

    def _is_id_kind_valid(self, id_kind: Any) -> bool:
        return id_kind is None or (
            NumberConstraints.is_int(id_kind) and NumberConstraints.positive(int(id_kind))
        )

    def _is_id_genre_valid(self, id_genre: Any) -> bool:
        return id_genre is None or (
            NumberConstraints.is_int(id_genre) and NumberConstraints.positive(int(id_genre))
        )

    def _is_release_year_valid(self, release_year: Any) -> bool:
        return release_year is None or (
            NumberConstraints.is_int(release_year) and NumberConstraints.positive(release_year)
        )

    def _is_price_valid(self, price: Any) -> bool:
        return price is None or (
            isinstance(price, dict)
            and self._is_min_price_valid(price.get('min'))
            and self._is_max_price_valid(price.get('max'))
        )

    def _is_min_price_valid(self, min_price: Any) -> bool:
        return min_price is None or (
            NumberConstraints.is_float(min_price)
            and NumberConstraints.positive(float(min_price))
            and NumberConstraints.decimal_precision_scale(
                float(min_price),
                precision=6,
                scale=2,
            )
        )

    def _is_max_price_valid(self, max_price: Any) -> bool:
        return max_price is None or (
            NumberConstraints.is_float(max_price)
            and NumberConstraints.positive(float(max_price))
            and NumberConstraints.decimal_precision_scale(
                float(max_price),
                precision=6,
                scale=2,
            )
        )

    def _set_fields(self, data: dict) -> None:
        filter: dict[str, Any | dict] | None = data.get('filter')

        self.query = data['query'].strip() if data.get('query') is not None else None

        if isinstance(filter, dict):
            self.filter['id_kind'] = (
                int(filter['id_kind']) if filter.get('id_kind') is not None else None
            )
            self.filter['id_genre'] = (
                int(filter['id_genre']) if filter.get('id_genre') is not None else None
            )
            self.filter['release_year'] = (
                int(filter['release_year']) if filter.get('release_year') is not None else None
            )

            price: dict | None = filter.get('price')

            if isinstance(price, dict):
                self.filter['price']['min'] = (
                    int(price['min']) if price.get('min') is not None else None
                )
                self.filter['price']['max'] = (
                    int(price['max']) if price.get('max') is not None else None
                )
