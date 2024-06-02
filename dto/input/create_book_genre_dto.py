from dto.base import InputDTO
from dto.constraints import StrConstraints
from exception import GeneralException


class CreateBookGenreDTO(InputDTO):
    genre: str

    def __init__(self) -> None:
        data = super()._get_json_data()
        self._validate_data(data)
        self._set_fields(data)

    def _validate_data(self, data: dict) -> None:
        new_genre = data.get('genre')

        if not (
            isinstance(new_genre, str)
            and StrConstraints.not_empty(new_genre)
            and StrConstraints.between_size(new_genre, min_size=3, max_size=30)
            and StrConstraints.match_pattern(
                new_genre, r'^[a-zA-ZáàãâäéèẽêëíìîĩïóòõôöúùũûüÁÀÃÂÄÉÈẼÊËÍÌÎĨÏÓÒÕÔÖÚÙŨÛÜç\s]+$'
            )
        ):
            raise GeneralException.InvalidDataSent()

    def _set_fields(self, data: dict) -> None:
        self.genre = data['genre'].strip().lower()
