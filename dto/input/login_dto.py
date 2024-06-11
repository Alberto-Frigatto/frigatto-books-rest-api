from typing import Any

from dto.base import InputDTO
from dto.constraints import StrConstraints
from exception import GeneralException


class LoginDTO(InputDTO):
    username: str
    password: str

    def __init__(self) -> None:
        data = super()._get_json_data()
        self._validate_data(data)
        self._set_fields(data)

    def _validate_data(self, data: dict) -> None:
        username = data.get('username')
        password = data.get('password')

        if not all(
            (
                self._are_request_fields_valid(data),
                self._is_username_valid(username),
                self._is_password_valid(password),
            )
        ):
            raise GeneralException.InvalidDataSent()

    def _are_request_fields_valid(self, data: dict) -> bool:
        fields = self.__annotations__.keys()

        return all(field in fields for field in data)

    def _is_username_valid(self, username: Any) -> bool:
        return isinstance(username, str) and StrConstraints.not_empty(username.strip())

    def _is_password_valid(self, password: Any) -> bool:
        return isinstance(password, str) and StrConstraints.not_empty(password.strip())

    def _set_fields(self, data: dict) -> None:
        self.username = data['username'].strip()
        self.password = data['password'].strip()
