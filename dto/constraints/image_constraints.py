from typing import Callable

from werkzeug.datastructures import FileStorage


class ImageConstraints:
    @staticmethod
    def quantity(image_list: list, min_qty: int, max_qty: int) -> bool:
        return min_qty <= len(image_list) <= max_qty

    @staticmethod
    def valid_image(img: FileStorage, validator: Callable) -> bool:
        return validator(img)
