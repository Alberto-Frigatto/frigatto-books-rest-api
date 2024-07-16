import os

from flask import Flask


def create_upload_dirs_if_dont_exist(app: Flask):
    dirs = (
        app.config['USER_PHOTOS_UPLOAD_DIR'],
        app.config['BOOK_PHOTOS_UPLOAD_DIR'],
    )

    for dir in dirs:
        os.makedirs(dir, exist_ok=True)
