from werkzeug.datastructures import FileStorage

from dto.base import InputDTO
from dto.constraints import ImageConstraints
from exception import GeneralException
from image_uploader import BookImageUploader


class CreateBookImgDTO(InputDTO):
    img: BookImageUploader

    def __init__(self) -> None:
        data = super()._get_files_data().to_dict()
        self._validate_data(data)
        self._set_fields(data)

    def _validate_data(self, data: dict) -> None:
        img: FileStorage | None = data.get('img')

        if not all((self._are_request_fields_valid(data), self._is_img_valid(img))):
            raise GeneralException.InvalidDataSent()

    def _are_request_fields_valid(self, data: dict) -> bool:
        fields = self.__annotations__.keys()

        return all(field in fields for field in data)

    def _is_img_valid(self, img: FileStorage | None) -> bool:
        return isinstance(img, FileStorage) and ImageConstraints.valid_image(
            img, BookImageUploader.validate_file
        )

    def _set_fields(self, data: dict) -> None:
        self.img = BookImageUploader(data['img'])
