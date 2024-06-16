from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from exception import GeneralException


class InputDTO(BaseModel):
    model_config = ConfigDict(extra='forbid')

    def __init__(self, **data: Any) -> None:
        try:
            super().__init__(**data)
        except ValidationError as e:
            raise GeneralException.InvalidDataSent(
                e.errors(include_url=False, include_context=False, include_input=False)
            )
