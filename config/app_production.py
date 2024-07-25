import os

SECRET_KEY = os.getenv('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{os.getenv("DB_USER", "root")}:{os.getenv("DB_PWD")}@{os.getenv("DB_HOST")}:3306/frigatto_books'
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_TOKEN_LOCATION = ['cookies']
UPLOAD_DIR = 'uploads'
USER_PHOTOS_UPLOAD_DIR = f'{UPLOAD_DIR}/users_photos'
BOOK_PHOTOS_UPLOAD_DIR = f'{UPLOAD_DIR}/books_photos'
PROPAGATE_EXCEPTIONS = True
