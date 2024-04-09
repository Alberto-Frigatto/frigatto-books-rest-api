from flask import Response
from flask_jwt_extended import JWTManager
from sqlalchemy import select

from api import api
from db import db
from models import User
from response import ResponseError

jwt = JWTManager()


@jwt.user_identity_loader
def user_identity_lookup(user: User) -> int:
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header: dict, jwt_data: dict) -> User | None:
    identity = jwt_data["sub"]

    return db.session.execute(select(User).filter_by(id=identity)).scalar_one_or_none()


@jwt.invalid_token_loader
def invalid_token_callback(error_string: str) -> Response:
    return ResponseError(api.errors.get('InvalidJWT')).json()


@jwt.unauthorized_loader
def unauthorized_callback(error_string: str) -> Response:
    error_map = {
        'CSRF double submit tokens do not match': 'InvalidCSFR',
        'Missing CSRF token': 'MissingCSFR',
        'Missing cookie "access_token_cookie"': 'MissingJWT',
    }

    return ResponseError(api.errors.get(error_map[error_string])).json()


# @jwt.
# def csrf_protected_callback(error_string) -> Response:
#     return ResponseError(api.errors.get('MissingCSFR')).json()
