from injector import inject
from sqlalchemy.orm import scoped_session

from exception import BookImgException
from image_uploader import BookImageUploader
from model import BookImg

from .. import IBookImgRepository


@inject
class BookImgRepository(IBookImgRepository):
    def __init__(self, session: scoped_session) -> None:
        self.session = session

    def get_by_id(self, id: str | int) -> BookImg:
        book_img = self.session.get(BookImg, id)

        if book_img is None:
            raise BookImgException.BookImgDoesntExists(str(id))

        return book_img

    def add(self, book_img: BookImg) -> None:
        self.session.add(book_img)
        self.session.commit()

    def delete(self, book_img: BookImg) -> None:
        self.session.delete(book_img)
        self.session.commit()

        BookImageUploader.delete(book_img.img_url)

    def update(self) -> None:
        self.session.commit()
