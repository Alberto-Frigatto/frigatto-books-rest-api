import os

JWT_SESSION_COOKIE = False
JWT_ACCESS_TOKEN_EXPIRES = False
JWT_COOKIE_SECURE = True
JWT_COOKIE_SAMESITE = "Strict"
RESPONSE_HEADERS = [
    ('Content-Type', 'application/json;charset=utf-8'),
    ('Access-Control-Allow-Origin', os.getenv('ALLOW-ORIGIN', 'http://127.0.0.1:5500')),
    ('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-CSRF-TOKEN'),
    ('Access-Control-Allow-Credentials', 'true'),
]
USER_PHOTOS_MAX_SIZE = 5 * 1024 * 1024
BOOK_PHOTOS_MAX_SIZE = 7 * 1024 * 1024
