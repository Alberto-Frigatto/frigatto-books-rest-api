from flask import Flask

from views import book_genres_bp, book_imgs_bp, book_keywords_bp, book_kinds_bp, books_bp, users_bp


def add_routes(app: Flask):
    app.register_blueprint(book_kinds_bp, url_prefix='/bookKinds', name='book_kinds')
    app.register_blueprint(users_bp, url_prefix='/users', name='users')
    app.register_blueprint(book_genres_bp, url_prefix='/bookGenres', name='book_genres')
    app.register_blueprint(books_bp, url_prefix='/books', name='books')
    app.register_blueprint(book_imgs_bp, url_prefix='/books', name='book_imgs')
    app.register_blueprint(book_keywords_bp, url_prefix='/books', name='book_keywords')
