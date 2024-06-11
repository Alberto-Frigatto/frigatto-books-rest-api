from dto.base import InputDTO
from dto.constraints import StrConstraints
from exception import GeneralException


class CreateBookKeywordDTO(InputDTO):
    keyword: str

    def __init__(self) -> None:
        data = super()._get_json_data()
        self._validate_data(data)
        self._set_fields(data)

    def _validate_data(self, data: dict) -> None:
        keyword = data.get('keyword')

        if not (
            isinstance(keyword, str)
            and StrConstraints.between_size(keyword, min_size=3, max_size=20)
            and StrConstraints.match_pattern(
                keyword, r'^[a-zA-ZáàãâäéèẽêëíìîĩïóòõôöúùũûüÁÀÃÂÄÉÈẼÊËÍÌÎĨÏÓÒÕÔÖÚÙŨÛÜç\s\d]+$'
            )
        ):
            raise GeneralException.InvalidDataSent()

    def _set_fields(self, data: dict) -> None:
        self.keyword = data['keyword'].strip().lower()
