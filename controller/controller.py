from abc import ABCMeta
from typing import Any

from flask import request

from exception import GeneralException


class Controller(metaclass=ABCMeta):
    def are_there_data(self) -> bool:
        return any(
            (
                request.form.to_dict(),
                request.files.to_dict(),
                request.get_json(silent=True),
            )
        )

    def get_json_data(self) -> Any | None:
        if not request.is_json:
            raise GeneralException.InvalidContentType()

        return request.json
