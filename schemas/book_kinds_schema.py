from models import BookKind

from .marshmallow import ma


class BookKindsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BookKind


book_kinds_schema = BookKindsSchema()
