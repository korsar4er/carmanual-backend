from flask import request
from flask_restful import Resource, reqparse, inputs
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from model import db, Doc, User
from schema import DocSchema
from helpers.upload_file import rm_obj_images

doc_schema = DocSchema()
docs_schema = DocSchema(many=True, exclude=('text',))

paginate_parser = reqparse.RequestParser()
paginate_parser.add_argument('page', type=int)
paginate_parser.add_argument('per_page', type=int)

filter_parser = reqparse.RequestParser()
filter_parser.add_argument('creator_id', type=int)
filter_parser.add_argument('approved', type=inputs.boolean)
filter_parser.add_argument('car_id', type=int)

doc_parser = reqparse.RequestParser()
doc_parser.add_argument('slug', required=True)
doc_parser.add_argument('car_id', type=int, required=True)
doc_parser.add_argument('part_id', type=int, required=True)


class DocsResource(Resource):
    def get(self):
        page_args = paginate_parser.parse_args()
        filter_args = filter_parser.parse_args()

        query = Doc.query
        for key, value in filter_args.items():
            if value is not None:
                if type(value) == bool:
                    query = query.filter(getattr(Doc, key).is_(value))
                else:
                    query = query.filter(getattr(Doc, key) == value)

        if page_args['page'] and page_args['per_page']:
            pagination = query.paginate(page_args['page'],
                                        page_args['per_page'])
            docs = pagination.items
            total = pagination.total
        else:
            docs = query.all()
            total = len(docs)
        docs_data = docs_schema.dump(docs)
        return {'status': 'success',
                'data': docs_data,
                'total': total}, 200


class DocByIdResource(Resource):
    def get(self, id):
        doc = Doc.query.filter_by(id=id).first()
        if not doc:
            return {'message': 'Doc does not found'}, 400
        doc_data = doc_schema.dump(doc)
        return {'status': 'success', 'data': doc_data}, 200

    @jwt_required
    def delete(self, id):
        doc = Doc.query.filter_by(id=id).first()
        if not doc:
            return {'message': 'Doc does not found'}, 400
        # check creator or admin
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if not user or (not user.is_admin() and user_id != doc.creator_id):
            return {'message': 'Admin role or creator required'}, 403
        # delete doc
        db.session.delete(doc)
        # delete image
        rm_obj_images(obj_type='doc', obj_id=doc.id)
        db.session.commit()
        return {}, 204


class DocResource(Resource):
    def get(self):
        args = doc_parser.parse_args()
        doc = Doc.query.filter_by(**args).first()
        if not doc:
            return {'message': 'Doc does not found'}, 400
        doc_data = doc_schema.dump(doc)
        return {'status': 'success', 'data': doc_data}, 200

    @jwt_required
    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        try:
            doc_data = doc_schema.load(json_data)
        except ValidationError as error:
            return {'message': error.messages}, 422
        duplicate = Doc.query.filter_by(slug=doc_data['slug'],
                                        car_id=doc_data['car_id'],
                                        part_id=doc_data['part_id']).first()
        if duplicate:
            return {'message':
                    'Уже есть документ с данным идентификатором'}, 409
        user_id = get_jwt_identity()
        doc = Doc(name=doc_data['name'],
                  slug=doc_data['slug'],
                  car_id=doc_data['car_id'],
                  part_id=doc_data['part_id'],
                  creator_id=user_id)
        db.session.add(doc)
        db.session.commit()
        doc_data = doc_schema.dump(doc)
        return {'status': 'success', 'data': doc_data}, 200

    @jwt_required
    def put(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        try:
            doc_id = json_data['id']
        except Exception:
            return {'message': 'Doc id does not found'}, 422

        doc = Doc.query.filter_by(id=doc_id).first()
        if not doc:
            return {'message': 'Doc does not found'}, 400
        # check creator or admin
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if not user or (not user.is_admin() and user_id != doc.creator_id):
            return {'message': 'Admin role or creator required'}, 403
        for key, value in json_data.items():
            setattr(doc, key, value)
        db.session.commit()
        return {}, 204
