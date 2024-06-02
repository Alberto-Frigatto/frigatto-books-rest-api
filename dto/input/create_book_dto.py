from datetime import datetime
from typing import Any

from werkzeug.datastructures import ImmutableMultiDict

from dto.base import InputDTO
from dto.constraints import ImageConstraints, NumberConstraints, StrConstraints
from exception import GeneralException
from image_uploader import BookImageUploader


class CreateBookDTO(InputDTO):
    name: str
    price: float
    author: str
    release_year: int
    keywords: list[str]
    id_book_kind: int
    id_book_genre: str
    imgs: list[BookImageUploader]

    def __init__(self) -> None:
        data = {
            'form': super()._get_form_data(),
            'files': super()._get_files_data(),
        }
        self._validate_data(data)
        self._set_fields(data)

    def _validate_data(self, data: dict) -> None:
        form_data: dict = data['form']
        files_data: ImmutableMultiDict = data['files']

        name = form_data.get('name')
        price = form_data.get('price')
        author = form_data.get('author')
        release_year = form_data.get('release_year')
        keywords = form_data.get('keywords')
        id_book_kind = form_data.get('id_book_kind')
        id_book_genre = form_data.get('id_book_genre')
        imgs = files_data.getlist('imgs')

        if not all(
            (
                self._are_request_fields_valid(data),
                self._is_name_valid(name),
                self._is_price_valid(price),
                self._is_author_valid(author),
                self._is_release_year_valid(release_year),
                self._are_keywords_valid(keywords),
                self._is_id_book_kind_valid(id_book_kind),
                self._is_id_book_genre_valid(id_book_genre),
                self._are_imgs_valid(imgs),
            )
        ):
            raise GeneralException.InvalidDataSent()

    def _are_request_fields_valid(self, data: dict) -> bool:
        fields = self.__annotations__.keys()
        form_data: dict = data['form']
        files_data: ImmutableMultiDict = data['files']

        return all(field in fields for field in form_data) and all(
            field in fields for field in files_data
        )

    def _is_name_valid(self, name: Any) -> bool:
        return (
            isinstance(name, str)
            and StrConstraints.not_empty(name.strip())
            and StrConstraints.between_size(name.strip(), min_size=2, max_size=80)
            and StrConstraints.match_pattern(
                name.strip(), r'^[a-zA-ZáàãâäéèẽêëíìîĩïóòõôöúùũûüÁÀÃÂÄÉÈẼÊËÍÌÎĨÏÓÒÕÔÖÚÙŨÛÜç\s\d-]+$'
            )
        )

    def _is_price_valid(self, price: Any) -> bool:
        return (
            NumberConstraints.is_float(price)
            and NumberConstraints.positive(float(price))
            and NumberConstraints.decimal_precision_scale(
                float(price),
                precision=6,
                scale=2,
            )
        )

    def _is_author_valid(self, author: Any) -> bool:
        return (
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
        return NumberConstraints.is_int(release_year) and NumberConstraints.between(
            int(release_year),
            min_value=1000,
            max_value=datetime.now().year,
        )

    def _are_keywords_valid(self, keywords: Any) -> bool:
        return (
            isinstance(keywords, str)
            and StrConstraints.not_empty(keywords.strip())
            and StrConstraints.match_pattern(
                keywords.strip(),
                r'^[a-zA-ZáàãâäéèẽêëíìîĩïóòõôöúùũûüÁÀÃÂÄÉÈẼÊËÍÌÎĨÏÓÒÕÔÖÚÙŨÛÜç\s\d-]',
            )
        )

    def _is_id_book_kind_valid(self, id_book_kind: Any) -> bool:
        return NumberConstraints.is_int(id_book_kind) and NumberConstraints.positive(
            int(id_book_kind)
        )

    def _is_id_book_genre_valid(self, id_book_genre: Any) -> bool:
        return NumberConstraints.is_int(id_book_genre) and NumberConstraints.positive(
            int(id_book_genre)
        )

    def _are_imgs_valid(self, imgs: list) -> bool:
        return ImageConstraints.quantity(imgs, min_qty=1, max_qty=5) and all(
            ImageConstraints.valid_image(img, BookImageUploader.validate_file) for img in imgs
        )

    def _set_fields(self, data: dict) -> None:
        form_data: dict[str, str | int | float] = data['form']
        files_data: ImmutableMultiDict = data['files']

        self.name = form_data['name'].strip()
        self.price = float(form_data['price'])
        self.author = form_data['author'].strip()
        self.release_year = int(form_data['release_year'])
        self.id_book_kind = int(form_data['id_book_kind'])
        self.id_book_genre = int(form_data['id_book_genre'])
        self.keywords = self._extract_book_keywords(form_data['keywords'])
        self.imgs = [BookImageUploader(img) for img in files_data.getlist('imgs')]

    def _extract_book_keywords(self, keywords: str) -> list[str]:
        separator = ';'

        return [keyword.strip() for keyword in keywords.strip().split(separator) if keyword]
