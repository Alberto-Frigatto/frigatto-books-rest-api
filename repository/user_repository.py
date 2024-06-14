from sqlalchemy import select

from db import db
from exception import UserException
from model import User


class UserRepository:
    def add(self, new_user: User) -> None:
        if self._user_already_exists(new_user.username):
            raise UserException.UserAlreadyExists()

        db.session.add(new_user)
        db.session.commit()

    def _user_already_exists(self, username: str | None) -> bool:
        with db.session.no_autoflush:
            query = select(User).where(User.username.ilike(username))

            return bool(db.session.execute(query).scalar())

    def update(self, updated_user: User) -> None:
        if self._was_username_modified(updated_user) and self._user_already_exists(
            updated_user.username
        ):
            raise UserException.UserAlreadyExists()

        db.session.commit()

    def _was_username_modified(self, updated_user: User) -> bool:
        with db.session.no_autoflush:
            query = select(User.username).filter_by(id=updated_user.id)
            old_username = db.session.execute(query).scalar()

            return updated_user.username != old_username

    def get_by_username(self, username: str) -> User | None:
        query = select(User).filter_by(username=username)

        return db.session.execute(query).scalar()
