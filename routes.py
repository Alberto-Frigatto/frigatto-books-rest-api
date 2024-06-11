from flask import Flask

from view import (
    auth_bp,
    book_bp,
    book_genre_bp,
    book_img_bp,
    book_keyword_bp,
    book_kind_bp,
    saved_book_bp,
    search_bp,
    user_bp,
)


def add_routes(app: Flask):
    app.register_blueprint(auth_bp, url_prefix='/auth', name='auth')
    app.register_blueprint(book_bp, url_prefix='/books', name='books')
    app.register_blueprint(book_genre_bp, url_prefix='/bookGenres', name='book_genres')
    app.register_blueprint(book_img_bp, url_prefix='/books', name='book_imgs')
    app.register_blueprint(book_keyword_bp, url_prefix='/books', name='book_keywords')
    app.register_blueprint(book_kind_bp, url_prefix='/bookKinds', name='book_kinds')
    app.register_blueprint(saved_book_bp, url_prefix='/books', name='saved_books')
    app.register_blueprint(search_bp, url_prefix='/search', name='searches')
    app.register_blueprint(user_bp, url_prefix='/users', name='users')
