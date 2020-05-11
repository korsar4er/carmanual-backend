from passlib.hash import pbkdf2_sha256 as sha256
from flask import request, current_app
from flask_restful import Resource
from marshmallow import ValidationError
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                jwt_required,
                                jwt_refresh_token_required,
                                get_jwt_identity)
from mail import send_confirm_mail, confirm_token
from model import db, User
from schema import UserSchema, UserRegistrationSchema
from decorators import is_enabled


user_schema = UserSchema()
user_reg_schema = UserRegistrationSchema()


class Registration(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        try:
            json_user = json_data["user"]
            url = json_data["url"]
        except Exception:
            return {'message': 'Url or user does not found in input data'}, 400
        # Validate and deserialize input
        try:
            user_data = user_reg_schema.load(json_user)
        except ValidationError as error:
            return {'message': error.messages}, 422
        duplicate = User.query.filter_by(name=user_data['name']).first()
        if duplicate:
            return {'message':
                    'Пользователь с таким именем уже существует'}, 409
        duplicate = User.query.filter_by(email=user_data['email']).first()
        if duplicate:
            return {'message':
                    'Пользователь с таким адресом почты уже существует'}, 409
        user = User(
            name=user_data['name'],
            email=user_data['email'],
            pass_hash=sha256.hash(user_data['password'])
        )
        if current_app.config['CONFIRM_USER_EMAIL']:
            try:
                send_confirm_mail(user.name, url, 'registration')
            except Exception as e:
                return {'message': 'Send confirm email error: ' + str(e)}, 500
        else:
            user.confirmed = True

        db.session.add(user)
        db.session.commit()
        result = user_schema.dump(user)

        return {"status": 'success', 'user': result}, 201


class Login(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        try:
            login = json_data['login']
            password = json_data['password']
        except Exception:
            return {'message': 'Login and password does not found'}, 400
        user = User.query.filter_by(name=login).first()
        if not user:
            return {'message': 'Пользователь не найден'}, 401
        if not user.confirmed:
            return {'message': 'Пользователь не подтвержден'}, 401
        if user.disabled:
            return {'message': 'Пользователь отключен'}, 401
        if sha256.verify(password, user.pass_hash):
            try:
                access_token = create_access_token(identity=user.id)
                refresh_token = create_refresh_token(identity=user.id)
                return {
                    "status": 'success',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    "user": user_schema.dump(user)
                }, 200
            except Exception as e:
                return {'message': 'Create token error: ' + str(e)}, 500
        else:
            return {'message': 'Неверный пароль'}, 401


class Confirm(Resource):
    def post(self, token):
        email = confirm_token(token, 'registration')
        if not email:
            return {'message': 'Load token error'}, 400
        rows = User.query.filter_by(name=email).update({"confirmed": True})
        if rows == 0:
            return {'message': 'User does not found'}, 400
        db.session.commit()

        return {}, 204


class ChangePassword(Resource):
    @jwt_required
    @is_enabled
    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        try:
            old_password = json_data['oldPassword']
            new_password = json_data['newPassword']
        except Exception:
            return {'message': 'Old or new passwords does not found'}, 422

        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {'message': 'User does not found'}, 422
        if sha256.verify(old_password, user.password):
            user.pass_hash = sha256.hash(new_password)
            db.session.commit()
            return {}, 204
        else:
            return {'message': 'Неверный пароль'}, 401


class ForgotPassword(Resource):
    def get(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        try:
            login = json_data['login']
            url = json_data['url']
        except Exception:
            return {'message': 'Login or url does not found'}, 400
        user = User.query.filter_by(name=login).first()
        if not user:
            return {'message': 'User does not found'}, 400
        if not user.confirmed:
            return {'message': 'User does not confirmed'}, 400
        if user.disabled:
            return {'message': 'User is disabled'}, 400
        try:
            send_confirm_mail(user.name, url, 'forgot_password')
        except Exception as e:
            return {'message': 'Send confirm email error: ' + str(e)}, 500

        return {}, 204

    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        try:
            token = json_data['token']
            password = json_data['password']
        except Exception:
            return {'message': 'Token or password does not found'}, 400
        email = confirm_token(token, 'forgot_password')
        if not email:
            return {'message': 'Load token error'}, 400
        user = User.query.filter_by(name=email).first()
        if not user:
            return {'message': 'User does not found'}, 400
        user.password = sha256.hash(password)
        db.session.commit()
        return {}, 204


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    @is_enabled
    def post(self):
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id)
        return {"status": 'success', 'access_token': access_token}, 200
