import re


class StrConstraints:
    @staticmethod
    def not_empty(value: str) -> bool:
        return bool(value)

    @staticmethod
    def between_size(value: str, *, min_size: int, max_size: int) -> bool:
        length = len(value)

        return min_size <= length <= max_size

    @staticmethod
    def match_pattern(value: str, pattern: str) -> bool:
        return bool(re.match(pattern, value))
