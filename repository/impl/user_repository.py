from injector import inject
from sqlalchemy import select

from db import IDbSession
from exception import UserException
from model import User

from .. import IUserRepository


@inject
class UserRepository(IUserRepository):
    def __init__(self, session: IDbSession) -> None:
        self.session = session

    def add(self, user: User) -> None:
        if self._user_already_exists(user.username):
            raise UserException.UserAlreadyExists()

        self.session.add(user)

    def _user_already_exists(self, username: str | None) -> bool:
        query = select(User).where(User.username.ilike(username))

        return bool(self.session.get_one(query))

    def update(self, user: User) -> None:
        if self._was_username_modified(user) and self._user_already_exists(user.username):
            raise UserException.UserAlreadyExists()

        self.session.update()

    def _was_username_modified(self, updated_user: User) -> bool:
        query = select(User.username).filter_by(id=updated_user.id)
        old_username = self.session.get_one(query)

        return updated_user.username != old_username

    def get_by_username(self, username: str) -> User | None:
        query = select(User).filter_by(username=username)

        return self.session.get_one(query)
