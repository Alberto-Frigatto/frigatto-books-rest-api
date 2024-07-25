from .base import ApiException


class BookImgException:
    class BookImgDoesntExist(ApiException):
        def __init__(self, id: str) -> None:
            super().__init__(
                message=f'The image {id} does not exist',
                status=404,
            )

    class BookDoesntOwnThisImg(ApiException):
        def __init__(self, id_img: str, id_book: str) -> None:
            super().__init__(
                message=f'The image {id_img} does not belong to the book {id_book}',
                status=403,
            )

    class BookMustHaveAtLeastOneImg(ApiException):
        def __init__(self, id_book: str) -> None:
            super().__init__(
                message=f'The book {id_book} must have at least one image',
                status=400,
            )

    class BookAlreadyHaveImageMaxQty(ApiException):
        def __init__(self, name: str) -> None:
            super().__init__(
                message=f'The book "{name}" already has the max quantity of images',
                status=400,
            )
