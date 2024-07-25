from typing import Any

from flask import request
from werkzeug.datastructures import FileStorage, ImmutableMultiDict

from exception import GeneralException


class Request:
    @classmethod
    def get_int_arg(cls, arg_name: str, default: int) -> int:
        return request.args.get(arg_name, default=default, type=int)

    @classmethod
    def get_json(cls) -> dict[str, Any]:
        if not cls._are_there_data():
            raise GeneralException.NoDataSent()

        if not request.is_json:
            raise GeneralException.InvalidContentType()

        if not isinstance(request.json, dict):
            raise GeneralException.InvalidDataSent()

        return request.json

    @classmethod
    def get_form(cls) -> ImmutableMultiDict[str, str]:
        if not cls._are_there_data():
            raise GeneralException.NoDataSent()

        return request.form

    @classmethod
    def get_files(cls) -> ImmutableMultiDict[str, FileStorage]:
        return request.files

    @classmethod
    def _are_there_data(cls) -> bool:
        return any(
            (
                request.form.to_dict(),
                request.files.to_dict(),
                request.get_json(silent=True),
            )
        )
