from typing import Any


class NumberConstraints:
    @staticmethod
    def positive(value: int | float) -> bool:
        return value > 0

    @staticmethod
    def between(value: int | float, *, min_value: int, max_value: int) -> bool:
        return min_value <= value <= max_value

    @staticmethod
    def is_int(value: Any) -> bool:
        try:
            int(value)
        except Exception as e:
            return False

        return True

    @staticmethod
    def is_float(value: Any) -> bool:
        try:
            float(value)
        except Exception as e:
            return False

        return True

    @classmethod
    def decimal_precision_scale(cls, value: float, *, precision: int, scale: int) -> bool:
        str_value = str(value)

        if not cls._is_smaller_or_eq_than_the_precision(str_value, precision):
            return False

        pos_decimal_sep = str_value.find('.')
        qty_decimal_digits = len(str_value) - pos_decimal_sep - 1

        return cls._is_smaller_or_eq_than_the_scale(qty_decimal_digits, scale)

    @classmethod
    def _is_smaller_or_eq_than_the_precision(cls, number: str, precision: int) -> bool:
        return len(number.replace('.', '')) <= precision

    @classmethod
    def _is_smaller_or_eq_than_the_scale(cls, qty_decimal_digits: int, scale: int) -> bool:
        return qty_decimal_digits <= scale
