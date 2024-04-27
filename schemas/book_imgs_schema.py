from marshmallow import fields

from models import BookImg

from .marshmallow import ma


class BookImgsSchema(ma.SQLAlchemySchema):
    class Meta:
        model = BookImg

    id = ma.auto_field()
    img_url = ma.auto_field()


book_imgs_schema = BookImgsSchema()
