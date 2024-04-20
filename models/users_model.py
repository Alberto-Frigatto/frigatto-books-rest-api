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
    img_url: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    def __init__(self, username: str, password: str, img_url: str) -> None:
        self._validate_username(username)
        self._validate_password(password)
        self._validate_img_url(img_url)

        self.username = self._format_text(username)
        self.password = generate_password_hash(self._format_text(password))
        self.img_url = self._format_text(img_url)

    def _validate_username(self, username: Any) -> None:
        if not self._is_username_valid(username):
            raise CustomError('InvalidDataSent')

    def _is_username_valid(self, username: Any) -> bool:
        min_length, max_length = 5, 50

        if not isinstance(username, str):
            return False

        username_length = len(username)

        return (
            username_length >= min_length
            and username_length <= max_length
            and re.match(r'^[a-zA-Z\d_-]+$', username)
        )

    def _validate_password(self, password: Any) -> None:
        if not self._is_password_valid(password):
            raise CustomError('InvalidDataSent')

    def _is_password_valid(self, password: Any) -> bool:
        min_length = 8

        return (
            isinstance(password, str)
            and len(password) >= min_length
            and self._password_has_necessary_chars(password)
        )

    def _password_has_necessary_chars(self, password: str) -> bool:
        has_uppercase = any(char.isupper() for char in password)
        has_lowercase = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_special = any(char in "!@#$%&*()_+=-,.:;?/\\|" for char in password)

        return all((has_uppercase, has_lowercase, has_digit, has_special))

    def _validate_img_url(self, img_url: Any) -> None:
        if not self._is_img_url_valid(img_url):
            raise CustomError('InvalidDataSent')

    def _is_img_url_valid(self, img_url: Any) -> bool:
        if not isinstance(img_url, str):
            return False

        img_url_length = len(img_url)

        min_length, max_length = 5, 255

        return img_url_length >= min_length and img_url_length <= max_length

    def _format_text(self, text: str) -> str:
        return text.strip()

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def update_username(self, username: str) -> None:
        self._validate_username(username)

        self.username = self._format_text(username)

    def update_password(self, password: str) -> None:
        self._validate_password(password)

        self.password = generate_password_hash(self._format_text(password))

    def update_img_url(self, img_url: str) -> None:
        self._validate_img_url(img_url)

        self.img_url = self._format_text(img_url)
