from db import db
from exception import BookImgException
from image_uploader import BookImageUploader
from model import BookImg


class BookImgRepository:
    def get_by_id(self, id: str | int) -> BookImg:
        book_img = db.session.get(BookImg, id)

        if book_img is None:
            raise BookImgException.BookImgDoesntExists(str(id))

        return book_img

    def add(self, new_book_img: BookImg) -> None:
        db.session.add(new_book_img)
        db.session.commit()

    def delete(self, book_img: BookImg) -> None:
        db.session.delete(book_img)
        db.session.commit()

        BookImageUploader.delete(book_img.img_url)

    def update(self) -> None:
        db.session.commit()
