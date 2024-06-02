from dto.base import InputDTO
from dto.constraints import StrConstraints
from exception import GeneralException


class UpdateBookKindDTO(InputDTO):
    kind: str

    def __init__(self) -> None:
        data = super()._get_json_data()
        self._validate_data(data)
        self._set_fields(data)

    def _validate_data(self, data: dict) -> None:
        new_kind = data.get('kind')

        if not (
            isinstance(new_kind, str)
            and StrConstraints.not_empty(new_kind)
            and StrConstraints.between_size(new_kind, min_size=3, max_size=30)
            and StrConstraints.match_pattern(
                new_kind, r'^[a-zA-ZáàãâäéèẽêëíìîĩïóòõôöúùũûüÁÀÃÂÄÉÈẼÊËÍÌÎĨÏÓÒÕÔÖÚÙŨÛÜç\s]+$'
            )
        ):
            raise GeneralException.InvalidDataSent()

    def _set_fields(self, data: dict) -> None:
        self.kind = data['kind'].strip().lower()
