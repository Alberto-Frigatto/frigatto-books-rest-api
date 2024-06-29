from flask import Response
from flask_jwt_extended import JWTManager

from db import db
from exception import SecurityException
from exception.base import ApiException
from model import User
from response import ErrorResponse

jwt = JWTManager()


@jwt.user_identity_loader
def user_identity_lookup(user: User) -> int:
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header: dict, jwt_data: dict) -> User | None:
    identity = jwt_data["sub"]

    return db.session.get(User, identity)


@jwt.invalid_token_loader
def invalid_token_callback(error_string: str) -> Response:
    return ErrorResponse(SecurityException.InvalidJWT()).json()


@jwt.unauthorized_loader
def unauthorized_callback(error_string: str) -> Response:
    error_map = {
        'CSRF double submit tokens do not match': 'InvalidCSFR',
        'Missing CSRF token': 'MissingCSFR',
        'Missing cookie "access_token_cookie"': 'MissingJWT',
        'Missing Authorization Header': 'MissingJWT',
    }

    exception: ApiException = getattr(SecurityException, error_map[error_string])()

    return ErrorResponse(exception).json()
