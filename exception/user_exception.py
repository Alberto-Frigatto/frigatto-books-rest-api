from .base import ApiException


class UserException:
    class UserAlreadyExists(ApiException):
        def __init__(self) -> None:
            super().__init__(
                name=self.__class__.__name__,
                message='This user already exists',
                status=409,
            )
