from injector import Binder
from sqlalchemy.orm import scoped_session

from db import db


def di_config(binder: Binder) -> None:
    binder.bind(scoped_session, db.session)
