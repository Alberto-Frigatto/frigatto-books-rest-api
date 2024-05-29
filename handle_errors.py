import importlib
import os

from flask_restful import Api


class CustomError(Exception):
    def __init__(self, error_name: str) -> None:
        self._error_name = error_name

    @property
    def error_name(self) -> str:
        return self._error_name

    def __str__(self) -> str:
        return self._error_name


def import_error_messages(api: Api):
    exception_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'exception'))

    for dirpath, _, filenames in os.walk(exception_dir):
        for filename in filenames:
            if f'_errors.py' in filename:
                module_path = os.path.splitext(
                    os.path.relpath(os.path.join(dirpath, filename), exception_dir)
                )[0]
                module_path = module_path.replace(os.path.sep, '.')
                module_path = f'exception.{module_path}'

                try:
                    module = importlib.import_module(module_path)
                    api.errors.update(module.errors)
                except ImportError:
                    pass
