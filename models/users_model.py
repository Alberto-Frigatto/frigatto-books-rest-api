import re
from typing import Any

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from db import db, int_pk
from handle_errors import CustomError


class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int_pk]
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    def __init__(self, username: str, password: str) -> None:
        self._validate_data(username, password)
        self.username = username.strip()
        self.password = generate_password_hash(password.strip())

    def _validate_data(self, username: Any, password: Any) -> None:
        if not self._is_username_valid(username) or not self._is_password_valid(password):
            raise CustomError('InvalidDataSent')

    def _is_username_valid(self, username: Any) -> bool:
        return (
            isinstance(username, str)
            and len(username) >= 5
            and re.match(r'^[a-zA-Z_\s]+$', username)
        )

    def _is_password_valid(self, password: Any) -> bool:
        if not isinstance(password, str) or len(password) < 8:
            return False

        return self._password_has_necessary_chars(password)

    def _password_has_necessary_chars(self, password: str) -> bool:
        has_uppercase = any(char.isupper() for char in password)
        has_lowercase = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_special = any(char in "!@#$%&*()_+=\-,.:;?/\\|" for char in password)

        return has_uppercase and has_lowercase and has_digit and has_special

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)
