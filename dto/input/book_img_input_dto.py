from pydantic import ConfigDict, field_validator
from werkzeug.datastructures import FileStorage

from dto.base import InputDTO
from image_uploader import BookImageUploader


class BookImgInputDTO(InputDTO):
    img: BookImageUploader

    model_config = ConfigDict(arbitrary_types_allowed=True, extra='forbid')

    @field_validator('img', mode='plain')
    def cast_img_to_UserImageUploader(cls, img: FileStorage) -> BookImageUploader:
        if not BookImageUploader.validate_file(img):
            raise ValueError('img is larger than 7MB or is not a image')

        return BookImageUploader(img)

    def __init__(self, **data: FileStorage) -> None:
        super().__init__(**data)
