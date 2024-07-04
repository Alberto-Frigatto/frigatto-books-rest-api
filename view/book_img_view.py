from flask import Blueprint, Response, send_file
from flask_jwt_extended import jwt_required

from controller import IBookImgController
from dto.input import BookImgInputDTO
from dto.output import BookImgOutputDTO
from utils.request import Request
from utils.response import SuccessResponse

book_img_bp = Blueprint('book_img_bp', __name__)


class BookImgView:
    @staticmethod
    @book_img_bp.get('/photos/<filename>')
    def get_book_img_by_filename(filename: str, controller: IBookImgController) -> Response:
        file_path, mimetype = controller.get_book_photo(filename)

        return send_file(file_path, mimetype)

    @staticmethod
    @book_img_bp.delete('/<id_book>/photos/<id_img>')
    @jwt_required()
    def delete_book_img(id_book: str, id_img: str, controller: IBookImgController) -> Response:
        controller.delete_book_img(id_book, id_img)

        return SuccessResponse().json()

    @staticmethod
    @book_img_bp.patch('/<id_book>/photos/<id_img>')
    @jwt_required()
    def update_book_img(id_book: str, id_img: str, controller: IBookImgController) -> Response:
        input_dto = BookImgInputDTO(**Request.get_files())

        updated_book_img = controller.update_book_img(id_book, id_img, input_dto)
        data = BookImgOutputDTO.dump(updated_book_img)

        return SuccessResponse(data).json()

    @staticmethod
    @book_img_bp.post('/<id_book>/photos')
    @jwt_required()
    def add_book_img(id_book: str, controller: IBookImgController) -> Response:
        input_dto = BookImgInputDTO(**Request.get_files())

        new_book_img = controller.create_book_img(id_book, input_dto)
        data = BookImgOutputDTO.dump(new_book_img)

        return SuccessResponse(data, 201).json()
