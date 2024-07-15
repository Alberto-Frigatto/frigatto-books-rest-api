from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from db import int_pk

from .base import Model


class User(Model):
    __tablename__ = 'users'

    id: Mapped[int_pk]
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    img_url: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    def __init__(self, username: str, password: str, img_url: str) -> None:
        self.username = username
        self.password = generate_password_hash(password)
        self.img_url = img_url

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def update_username(self, username: str) -> None:
        self.username = username

    def update_password(self, password: str) -> None:
        self.password = generate_password_hash(password)

    def update_img_url(self, img_url: str) -> None:
        self.img_url = img_url
