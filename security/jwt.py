from flask_jwt_extended import JWTManager

from db import db
from model import User

jwt = JWTManager()


@jwt.user_identity_loader
def user_identity_lookup(user: User) -> int:
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header: dict, jwt_data: dict) -> User | None:
    identity = jwt_data["sub"]

    return db.session.get(User, identity)
