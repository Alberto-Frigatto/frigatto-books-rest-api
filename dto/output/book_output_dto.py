from dto.base import OutputDTO

from .book_genre_output_dto import BookGenreOutputDTO
from .book_img_output_dto import BookImgOutputDTO
from .book_keyword_output_dto import BookKeywordOutputDTO
from .book_kind_output_dto import BookKindOutputDTO


class BookOutputDTO(OutputDTO):
    id: int
    name: str
    price: float
    author: str
    release_year: int
    book_genre: BookGenreOutputDTO
    book_kind: BookKindOutputDTO
    book_keywords: list[BookKeywordOutputDTO]
    book_imgs: list[BookImgOutputDTO]
