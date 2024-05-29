from model import BookGenre

from .marshmallow import ma


class BookGenresSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BookGenre


book_genres_schema = BookGenresSchema()
