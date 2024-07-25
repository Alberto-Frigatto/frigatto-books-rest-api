from .base import ApiException, ValidationException


class ImageException:
    class ImageNotFound(ApiException):
        def __init__(self, filename: str) -> None:
            super().__init__(
                message=f'The image {filename} was not found',
                status=404,
            )

    class ImagesArentFiles(ValidationException):
        def __init__(self) -> None:
            super().__init__('The provided images are not files')

    class ImageIsNotAFile(ValidationException):
        def __init__(self) -> None:
            super().__init__('The provided image is not a file')

    class FileIsNotAnImage(ValidationException):
        def __init__(self) -> None:
            super().__init__('The provided file is not an image')

    class ImageIsTooLarge(ValidationException):
        def __init__(self, max_size_mb: int) -> None:
            super().__init__(f'The provided image is larger than {max_size_mb}MB')
