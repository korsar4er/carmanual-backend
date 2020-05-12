import os

basedir = os.path.abspath(os.path.dirname(__file__))

PROPAGATE_EXCEPTIONS = True

SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite3"

JWT_SECRET_KEY = "my-jwt-secret-string"
JWT_ACCESS_TOKEN_EXPIRES = 60 * 30  # 60 * 24
JWT_REFRESH_TOKEN_EXPIRES = 60 * 60 * 24  # * 30

SERIALIZER_SECRET_KEY = "my-secret-string"

MAIL_SERVER = "smtp.mail.yahoo.com"
MAIL_PORT = 465  # 587
MAIL_USE_TLS = False
MAIL_USE_SSL = True
# MAIL_DEBUG : default app.debug
MAIL_USERNAME = "email.confirm@yahoo.com"
MAIL_PASSWORD = "phoknazdfafkevjw"
# DEFAULT_MAIL_SENDER = ("email confirm sender", "confirm.email.76@yandex.com")
CONFIRM_MAIL_SENDER = ("Email confirm sender", "email.confirm@yahoo.com")

CONFIRM_USER_EMAIL = False

UPLOAD_IMAGE_DIR = os.path.join(basedir, 'upload', 'images')
UPLOAD_IMAGE_URL = '/images'
