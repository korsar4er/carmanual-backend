from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from model import db, Part
from schema import PartSchema
from decorators import roles_required

part_schema = PartSchema()
parts_schema = PartSchema(many=True)


class PartsResource(Resource):
    def get(self):
        parts = Part.query.all()
        parts_data = parts_schema.dump(parts)
        return {'status': 'success', 'data': parts_data}, 200


class PartResource(Resource):
    @jwt_required
    @roles_required('admin')
    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        try:
            part_data = part_schema.load(json_data)
        except ValidationError as error:
            return {'message': error.messages}, 422

        duplicate = Part.query.filter_by(name=part_data['name']).first()
        if duplicate:
            return {'message': 'Уже есть раздел с таким наименованием'}, 409
        duplicate = Part.query.filter_by(slug=part_data['slug']).first()
        if duplicate:
            return {'message': 'Уже есть раздел с таким идентификатором'}, 409

        part = Part(name=part_data['name'], slug=part_data['slug'])
        db.session.add(part)
        db.session.commit()
        part_data = part_schema.dump(part)
        return {'status': 'success', 'data': part_data}, 200

    @jwt_required
    @roles_required('admin')
    def put(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        try:
            id = json_data['id']
        except Exception:
            return {'message': 'Id does not found'}, 400
        rows = Part.query.filter_by(id=id).update(json_data)
        if rows == 0:
            return {'message': 'Part does not found'}, 400
        db.session.commit()
        return {}, 204

    @jwt_required
    @roles_required('admin')
    def delete(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        try:
            id = json_data['id']
        except Exception:
            return {'message': 'Id does not found'}, 400
        rows = Part.query.filter_by(id=id).delete()
        if rows == 0:
            return {'message': 'Part does not found'}, 400
        db.session.commit()
        return {}, 204
