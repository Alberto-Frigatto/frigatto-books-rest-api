from model import Book

from .book_genres_schema import BookGenresSchema
from .book_imgs_schema import BookImgsSchema
from .book_keywords_schema import BookKeywordsSchema
from .book_kinds_schema import BookKindsSchema
from .marshmallow import ma


class BooksSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Book

    id = ma.auto_field()
    name = ma.auto_field()
    price = ma.Float()
    author = ma.auto_field()
    release_year = ma.auto_field()
    book_genre = ma.Nested(BookGenresSchema)
    book_kind = ma.Nested(BookKindsSchema)
    book_keywords = ma.Nested(BookKeywordsSchema, many=True)
    book_imgs = ma.Nested(BookImgsSchema, many=True)


books_schema = BooksSchema()
