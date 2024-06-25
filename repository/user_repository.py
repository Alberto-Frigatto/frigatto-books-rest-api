from injector import inject
from sqlalchemy import select
from sqlalchemy.orm import scoped_session

from exception import UserException
from model import User


@inject
class UserRepository:
    def __init__(self, session: scoped_session) -> None:
        self.session = session

    def add(self, new_user: User) -> None:
        if self._user_already_exists(new_user.username):
            raise UserException.UserAlreadyExists()

        self.session.add(new_user)
        self.session.commit()

    def _user_already_exists(self, username: str | None) -> bool:
        with self.session.no_autoflush:
            query = select(User).where(User.username.ilike(username))

            return bool(self.session.execute(query).scalar())

    def update(self, updated_user: User) -> None:
        if self._was_username_modified(updated_user) and self._user_already_exists(
            updated_user.username
        ):
            raise UserException.UserAlreadyExists()

        self.session.commit()

    def _was_username_modified(self, updated_user: User) -> bool:
        with self.session.no_autoflush:
            query = select(User.username).filter_by(id=updated_user.id)
            old_username = self.session.execute(query).scalar()

            return updated_user.username != old_username

    def get_by_username(self, username: str) -> User | None:
        query = select(User).filter_by(username=username)

        return self.session.execute(query).scalar()
