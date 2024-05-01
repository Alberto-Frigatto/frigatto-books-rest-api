from marshmallow import fields

from models import BookKeyword

from .marshmallow import ma


class BookKeywordsSchema(ma.SQLAlchemySchema):
    class Meta:
        model = BookKeyword

    id = ma.auto_field()
    keyword = ma.auto_field()


book_keywords_schema = BookKeywordsSchema()
