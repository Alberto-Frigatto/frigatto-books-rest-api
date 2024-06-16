from flask import Blueprint, Response, send_file
from flask_jwt_extended import jwt_required

from controller import BookImgController
from dto.input import BookImgInputDTO
from exception.base import ApiException
from request import Request
from response import ResponseError, ResponseSuccess
from schema import book_imgs_schema

book_img_bp = Blueprint('book_img_bp', __name__)


class BookImgView:
    controller = BookImgController()

    @staticmethod
    @book_img_bp.get('/photos/<filename>')
    def get_book_img_by_filename(filename: str) -> Response:
        try:
            file_path, mimetype = BookImgView.controller.get_book_photo(filename)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            return send_file(file_path, mimetype)

    @staticmethod
    @book_img_bp.delete('/<id_book>/photos/<id_img>')
    @jwt_required()
    def delete_book_img(id_book: str, id_img: str) -> Response:
        try:
            BookImgView.controller.delete_book_img(id_book, id_img)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            return ResponseSuccess().json()

    @staticmethod
    @book_img_bp.patch('/<id_book>/photos/<id_img>')
    @jwt_required()
    def update_book_img(id_book: str, id_img: str) -> Response:
        try:
            input_dto = BookImgInputDTO(**Request.get_files())
            updated_book_img = BookImgView.controller.update_book_img(id_book, id_img, input_dto)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = book_imgs_schema.dump(updated_book_img)

            return ResponseSuccess(data).json()

    @staticmethod
    @book_img_bp.post('/<id_book>/photos')
    @jwt_required()
    def add_book_img(id_book: str) -> Response:
        try:
            input_dto = BookImgInputDTO(**Request.get_files())
            new_book_img = BookImgView.controller.create_book_img(id_book, input_dto)
        except ApiException as e:
            return ResponseError(e).json()
        else:
            data = book_imgs_schema.dump(new_book_img)

            return ResponseSuccess(data, 201).json()
