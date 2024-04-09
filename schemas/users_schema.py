from models import User

from .marshmallow import ma


class UsersSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = ma.auto_field()
    username = ma.auto_field()


users_schema = UsersSchema()
