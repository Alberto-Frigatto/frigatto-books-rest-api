from flask import Blueprint, Response, send_file
from flask_jwt_extended import jwt_required
from flask_restful import Api

from api import BaseResource
from controllers import BookImgsController
from handle_errors import CustomError
from response import ResponseError, ResponseSuccess
from schemas import book_imgs_schema

book_imgs_bp = Blueprint('books_bp', __name__)
book_imgs_api = Api(book_imgs_bp)

controller = BookImgsController()


class GetBooksPhotosView(BaseResource):
    def get(self, filename: str) -> Response:
        try:
            file_path, mimetype = controller.get_book_photo(filename)
        except CustomError as e:
            return ResponseError(e).json()
        else:
            return send_file(file_path, mimetype)


class EditBooksPhotosView(BaseResource):
    @jwt_required()
    def delete(self, id_book: int, id_img: int) -> Response:
        try:
            controller.delete_book_img(id_book, id_img)
        except CustomError as e:
            return ResponseError(e).json()
        else:
            return ResponseSuccess().json()

    @jwt_required()
    def patch(self, id_book: int, id_img: int) -> Response:
        try:
            updated_book_img = controller.update_book_img(id_book, id_img)
        except CustomError as e:
            return ResponseError(e).json()
        else:
            data = book_imgs_schema.dump(updated_book_img)

            return ResponseSuccess(data).json()


class AddBooksPhotosView(BaseResource):
    @jwt_required()
    def post(self, id_book: int) -> Response:
        try:
            new_book_img = controller.create_book_img(id_book)
        except CustomError as e:
            return ResponseError(e).json()
        else:
            data = book_imgs_schema.dump(new_book_img)

            return ResponseSuccess(data, 201).json()


book_imgs_api.add_resource(GetBooksPhotosView, '/photos/<string:filename>')
book_imgs_api.add_resource(
    EditBooksPhotosView,
    '/<int:id_book>/photos/<int:id_img>',
    '/<string:id_book>/photos/<string:id_img>',
)
book_imgs_api.add_resource(
    AddBooksPhotosView,
    '/<int:id_book>/photos',
    '/<string:id_book>/photos',
)
