from flask import Flask
from flask_jwt_extended import JWTManager


def create_app(config_filename):

    app = Flask(__name__)
    app.config.from_object(config_filename)

    from api import api
    api.init_app(app)

    from model import db
    db.init_app(app)

    # from jwt_ext import jwt
    jwt = JWTManager()
    jwt.init_app(app)

    from mail import mail
    mail.init_app(app)

    return app


if __name__ == '__main__':
    app = create_app("config")
    app.run(debug=True)