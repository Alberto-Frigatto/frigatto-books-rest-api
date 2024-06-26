from abc import ABC, abstractmethod

from model import BookImg


class IBookImgRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> BookImg:
        pass

    @abstractmethod
    def add(self, book_img: BookImg) -> None:
        pass

    @abstractmethod
    def delete(self, book_img: BookImg) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass
