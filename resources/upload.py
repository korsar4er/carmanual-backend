import werkzeug
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from helpers.upload_file import upload_image


class UploadImage(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('image', type=werkzeug.datastructures.FileStorage,
                            location='files', required=True)
        parser.add_argument('object_type',
                            location='form', required=True)
        parser.add_argument('object_id', type=int,
                            location='form', required=True)
        args = parser.parse_args()

        try:
            url = upload_image(file_storage=args['image'],
                               obj_type=args['object_type'],
                               obj_id=args['object_id'])
        except Exception as error:
            return {'message': str(error)}, 500

        return {'message': 'success', 'data': url}, 200
