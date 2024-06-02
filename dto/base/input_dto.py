from abc import ABCMeta, abstractmethod

from flask import request
from werkzeug.datastructures import ImmutableMultiDict

from exception import GeneralException


class InputDTO(metaclass=ABCMeta):
    @abstractmethod
    def _validate_data(self, data: dict) -> None:
        pass

    @abstractmethod
    def _set_fields(self, data: dict) -> None:
        pass

    def _are_there_data(self) -> bool:
        return any(
            (
                request.form.to_dict(),
                request.files.to_dict(),
                request.get_json(silent=True),
            )
        )

    def _get_json_data(self) -> dict:
        if not self._are_there_data():
            raise GeneralException.NoDataSent()

        if not request.is_json:
            raise GeneralException.InvalidContentType()

        if not isinstance(request.json, dict):
            raise GeneralException.InvalidDataSent()

        return request.json

    def _get_form_data(self) -> dict:
        if not self._are_there_data():
            raise GeneralException.NoDataSent()

        return request.form.to_dict()

    def _get_files_data(self) -> ImmutableMultiDict:
        if not self._are_there_data():
            raise GeneralException.NoDataSent()

        return request.files
