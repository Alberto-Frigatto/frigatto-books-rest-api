import os

from flask import Flask


def create_upload_dirs_if_dont_exist(app: Flask):
    directories = (
        app.config['USER_PHOTOS_UPLOAD_DIR'],
        app.config['BOOK_PHOTOS_UPLOAD_DIR'],
    )

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
