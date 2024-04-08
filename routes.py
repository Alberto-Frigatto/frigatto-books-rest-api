from flask import Flask

from views import book_kinds_bp


def add_routes(app: Flask):
    app.register_blueprint(book_kinds_bp, url_prefix='/bookKinds')
