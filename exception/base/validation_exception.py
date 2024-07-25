class ValidationException(ValueError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
