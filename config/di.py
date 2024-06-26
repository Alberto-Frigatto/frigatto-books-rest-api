from injector import Binder, singleton
from sqlalchemy.orm import scoped_session

from controller import (
    IAuthController,
    IBookController,
    IBookGenreController,
    IBookImgController,
    IBookKeywordController,
    IBookKindController,
    ISavedBookController,
    ISearchController,
    IUserController,
)
from controller.impl import (
    AuthController,
    BookController,
    BookGenreController,
    BookImgController,
    BookKeywordController,
    BookKindController,
    SavedBookController,
    SearchController,
    UserController,
)
from db import db
from repository import (
    IBookGenreRepository,
    IBookImgRepository,
    IBookKeywordRepository,
    IBookKindRepository,
    IBookRepository,
    ISavedBookRepository,
    ISearchRepository,
    IUserRepository,
)
from repository.impl import (
    BookGenreRepository,
    BookImgRepository,
    BookKeywordRepository,
    BookKindRepository,
    BookRepository,
    SavedBookRepository,
    SearchRepository,
    UserRepository,
)
from service import (
    IAuthService,
    IBookGenreService,
    IBookImgService,
    IBookKeywordService,
    IBookKindService,
    IBookService,
    ISavedBookService,
    ISearchService,
    IUserService,
)
from service.impl import (
    AuthService,
    BookGenreService,
    BookImgService,
    BookKeywordService,
    BookKindService,
    BookService,
    SavedBookService,
    SearchService,
    UserService,
)


def di_config(binder: Binder) -> None:
    binder.bind(scoped_session, to=db.session, scope=singleton)

    binder.bind(IBookGenreRepository, to=BookGenreRepository, scope=singleton)
    binder.bind(IBookImgRepository, to=BookImgRepository, scope=singleton)
    binder.bind(IBookKeywordRepository, to=BookKeywordRepository, scope=singleton)
    binder.bind(IBookKindRepository, to=BookKindRepository, scope=singleton)
    binder.bind(IBookRepository, to=BookRepository, scope=singleton)
    binder.bind(ISavedBookRepository, to=SavedBookRepository, scope=singleton)
    binder.bind(ISearchRepository, to=SearchRepository, scope=singleton)
    binder.bind(IUserRepository, to=UserRepository, scope=singleton)

    binder.bind(IAuthService, to=AuthService, scope=singleton)
    binder.bind(IBookGenreService, to=BookGenreService, scope=singleton)
    binder.bind(IBookImgService, to=BookImgService, scope=singleton)
    binder.bind(IBookKeywordService, to=BookKeywordService, scope=singleton)
    binder.bind(IBookKindService, to=BookKindService, scope=singleton)
    binder.bind(IBookService, to=BookService, scope=singleton)
    binder.bind(ISavedBookService, to=SavedBookService, scope=singleton)
    binder.bind(ISearchService, to=SearchService, scope=singleton)
    binder.bind(IUserService, to=UserService, scope=singleton)

    binder.bind(IAuthController, to=AuthController, scope=singleton)
    binder.bind(IBookController, to=BookController, scope=singleton)
    binder.bind(IBookGenreController, to=BookGenreController, scope=singleton)
    binder.bind(IBookImgController, to=BookImgController, scope=singleton)
    binder.bind(IBookKeywordController, to=BookKeywordController, scope=singleton)
    binder.bind(IBookKindController, to=BookKindController, scope=singleton)
    binder.bind(ISavedBookController, to=SavedBookController, scope=singleton)
    binder.bind(ISearchController, to=SearchController, scope=singleton)
    binder.bind(IUserController, to=UserController, scope=singleton)
