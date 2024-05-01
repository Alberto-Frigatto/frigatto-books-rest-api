from abc import ABCMeta

from flask import request


class Controller(metaclass=ABCMeta):
    def are_there_data(self) -> bool:
        return any(
            (
                request.form.to_dict(),
                request.files.to_dict(),
                request.get_json(silent=True),
            )
        )
