from datetime import datetime
from typing import Any

from dto.base import InputDTO
from dto.constraints import NumberConstraints, StrConstraints
from exception import GeneralException


class UpdateBookDTO(InputDTO):
    name: str | None
    price: float | None
    author: str | None
    release_year: int | None
    id_book_kind: int | None
    id_book_genre: str | None

    def __init__(self) -> None:
        data = super()._get_form_data()
        self._validate_data(data)
        self._set_fields(data)

    def _validate_data(self, data: dict) -> None:
        name = data.get('name')
        price = data.get('price')
        author = data.get('author')
        release_year = data.get('release_year')
        id_book_kind = data.get('id_book_kind')
        id_book_genre = data.get('id_book_genre')

        if not all(
            (
                self._are_request_fields_valid(data),
                self._is_name_valid(name),
                self._is_price_valid(price),
                self._is_author_valid(author),
                self._is_release_year_valid(release_year),
                self._is_id_book_kind_valid(id_book_kind),
                self._is_id_book_genre_valid(id_book_genre),
            )
        ):
            raise GeneralException.InvalidDataSent()

    def _are_request_fields_valid(self, data: dict) -> bool:
        fields = self.__annotations__.keys()

        return all(field in fields for field in data)

    def _is_name_valid(self, name: Any) -> bool:
        return name is None or (
            isinstance(name, str)
            and StrConstraints.not_empty(name.strip())
            and StrConstraints.between_size(name.strip(), min_size=2, max_size=80)
            and StrConstraints.match_pattern(
                name.strip(), r'^[a-zA-ZáàãâäéèẽêëíìîĩïóòõôöúùũûüÁÀÃÂÄÉÈẼÊËÍÌÎĨÏÓÒÕÔÖÚÙŨÛÜç\s\d-]+$'
            )
        )

    def _is_price_valid(self, price: Any) -> bool:
        return price is None or (
            NumberConstraints.is_float(price)
            and NumberConstraints.positive(float(price))
            and NumberConstraints.decimal_precision_scale(
                float(price),
                precision=6,
                scale=2,
            )
        )

    def _is_author_valid(self, author: Any) -> bool:
        return author is None or (
            isinstance(author, str)
            and StrConstraints.not_empty(author.strip())
            and StrConstraints.between_size(
                author.strip(),
                min_size=3,
                max_size=40,
            )
            and StrConstraints.match_pattern(
                author.strip(), r'^[a-zA-ZáàãâäéèẽêëíìîĩïóòõôöúùũûüÁÀÃÂÄÉÈẼÊËÍÌÎĨÏÓÒÕÔÖÚÙŨÛÜç\s]+$'
            )
        )

    def _is_release_year_valid(self, release_year: Any) -> bool:
        return (
            release_year is None
            or NumberConstraints.is_int(release_year)
            and NumberConstraints.between(
                int(release_year),
                min_value=1000,
                max_value=datetime.now().year,
            )
        )

    def _is_id_book_kind_valid(self, id_book_kind: Any) -> bool:
        return (
            id_book_kind is None
            or NumberConstraints.is_int(id_book_kind)
            and NumberConstraints.positive(int(id_book_kind))
        )

    def _is_id_book_genre_valid(self, id_book_genre: Any) -> bool:
        return (
            id_book_genre is None
            or NumberConstraints.is_int(id_book_genre)
            and NumberConstraints.positive(int(id_book_genre))
        )

    def _set_fields(self, data: dict) -> None:
        self.name = data['name'].strip() if data.get('name') is not None else None
        self.price = float(data['price']) if data.get('price') is not None else None
        self.author = data['author'].strip() if data.get('author') is not None else None
        self.release_year = (
            int(data['release_year']) if data.get('release_year') is not None else None
        )
        self.id_book_kind = (
            int(data['id_book_kind']) if data.get('id_book_kind') is not None else None
        )
        self.id_book_genre = (
            int(data['id_book_genre']) if data.get('id_book_genre') is not None else None
        )
