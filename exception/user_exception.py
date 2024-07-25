from .base import ApiException, ValidationException


class UserException:
    class UserAlreadyExists(ApiException):
        def __init__(self) -> None:
            super().__init__(
                message='This user already exists',
                status=409,
            )

    class PasswordTooShort(ValidationException):
        def __init__(self, min_chars: int) -> None:
            super().__init__(f'The provided password should have at least {min_chars} characters')

    class PasswordTooLong(ValidationException):
        def __init__(self, max_chars: int) -> None:
            super().__init__(f'The provided password should have at most {max_chars} characters')

    class PasswordWithoutNecessaryChars(ValidationException):
        def __init__(self) -> None:
            super().__init__('The provided password has not the necessary chars')
