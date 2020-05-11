from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from model import db, User
from schema import UserSchema
from decorators import roles_required

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class UsersResource(Resource):
    @jwt_required
    @roles_required("admin")
    def get(self):
        users = User.query.all()
        users_data = users_schema.dump(users)
        return {'status': 'success', 'data': users_data}, 200


class UserResource(Resource):

    @jwt_required
    @roles_required("admin")
    def put(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        try:
            user_data = user_schema.load(json_data)
        except ValidationError as error:
            return {'message': error.messages}, 422
        rows = User.query.filter_by(id=user_data['id']).update(user_data)
        if rows == 0:
            return {'message': 'User does not exist'}, 400
        db.session.commit()

        return {}, 204

    @jwt_required
    @roles_required("admin")
    def delete(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        try:
            user_id = json_data['id']
        except Exception:
            return {'message': 'User ID does not found'}, 400
        rows = User.query.filter_by(id=user_id).delete()
        if rows == 0:
            return {'message': 'User does not exist'}, 400

        db.session.commit()
        return {}, 204
