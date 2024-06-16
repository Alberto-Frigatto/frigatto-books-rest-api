from typing import Any

from pydantic import Field

from dto.base import InputDTO


class LoginInputDTO(InputDTO):
    username: str = Field(strict=True)
    password: str = Field(strict=True)

    def __init__(self, **data: str | Any) -> None:
        super().__init__(**data)
