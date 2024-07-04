from injector import inject

from db import IDbSession
from exception import BookImgException
from model import BookImg
from utils.file.uploader import BookImageUploader

from .. import IBookImgRepository


@inject
class BookImgRepository(IBookImgRepository):
    def __init__(self, session: IDbSession) -> None:
        self.session = session

    def get_by_id(self, id: str) -> BookImg:
        book_img = self.session.get_by_id(BookImg, id)

        if book_img is None:
            raise BookImgException.BookImgDoesntExists(str(id))

        return book_img

    def add(self, book_img: BookImg) -> None:
        self.session.add(book_img)

    def delete(self, book_img: BookImg) -> None:
        self.session.delete(book_img)

        BookImageUploader.delete(book_img.img_url)

    def update(self) -> None:
        self.session.update()
