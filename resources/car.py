import werkzeug
from flask_restful import Resource, reqparse, inputs
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, Car, User
from schema import CarSchema
from helpers.upload_file import upload_image, rm_obj_images
from decorators import roles_required

car_schema = CarSchema()
cars_schema = CarSchema(many=True)

paginate_parser = reqparse.RequestParser()
paginate_parser.add_argument('page', type=int)
paginate_parser.add_argument('per_page', type=int)

filter_parser = reqparse.RequestParser()
filter_parser.add_argument('creator_id', type=int)
filter_parser.add_argument('approved', type=inputs.boolean)

post_parser = reqparse.RequestParser()
post_parser.add_argument('image',
                         type=werkzeug.datastructures.FileStorage,
                         location='files')
post_parser.add_argument('name', location='form', required=True)
post_parser.add_argument('slug', location='form', required=True)

put_parser = reqparse.RequestParser()
put_parser.add_argument('image',
                        type=werkzeug.datastructures.FileStorage,
                        location='files')
put_parser.add_argument('id', type=int, location='form', required=True)
put_parser.add_argument('name', location='form')
put_parser.add_argument('slug', location='form')

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, required=True)


class CarsResourse(Resource):
    def get(self):
        filter_args = filter_parser.parse_args()
        page_args = paginate_parser.parse_args()

        query = Car.query
        for key, value in filter_args.items():
            if value is not None:
                if type(value) == bool:
                    query = query.filter(getattr(Car, key).is_(value))
                else:
                    query = query.filter(getattr(Car, key) == value)

        if page_args['page'] and page_args['per_page']:
            pagination = query.paginate(page_args['page'],
                                        page_args['per_page'])
            cars = pagination.items
            total = pagination.total
        else:
            cars = query.all()
            total = len(cars)
        cars_data = cars_schema.dump(cars)
        return {'status': 'success',
                'data': cars_data,
                'total': total}, 200


class CarResourse(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(name='id', type=int)
        parser.add_argument(name='slug')
        args = parser.parse_args()
        if args["id"]:
            car = Car.query.filter_by(id=args["id"]).first()
        elif args["slug"]:
            car = Car.query.filter_by(slug=args["slug"]).first()
        else:
            return {'message': 'Id or slug required'}, 400
        if not car:
            return {'message': 'Car does not found'}, 400
        car_data = car_schema.dump(car)
        return {'status': 'success', 'data': car_data}, 200

    @jwt_required
    def post(self):
        args = post_parser.parse_args()
        # add car
        duplicate = Car.query.filter_by(name=args['name']).first()
        if duplicate:
            return {'message':
                    'Уже есть автомобиль с данным наименованием'}, 409
        duplicate = Car.query.filter_by(slug=args['slug']).first()
        if duplicate:
            return {'message':
                    'Уже есть автомобиль с данным идентификатором'}, 409
        user_id = get_jwt_identity()
        car = Car(name=args['name'],
                  slug=args['slug'],
                  creator_id=user_id)
        db.session.add(car)

        # save car image
        image = args['image']
        if image:
            db.session.flush()  # for car.id
            try:
                url = upload_image(file_storage=image,
                                   obj_type='car',
                                   obj_id=car.id)
            except Exception as error:
                return {'message': str(error)}, 500
            car.img_src = url

        db.session.commit()
        car_data = car_schema.dump(car)
        return {'status': 'success', 'data': car_data}, 200

    @jwt_required
    def put(self):
        args = put_parser.parse_args()
        car = Car.query.filter_by(id=args['id']).first()
        if not car:
            return {'message': 'Car does not found'}, 400
        # check creator or admin
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if not user or (not user.is_admin() and user_id != car.creator_id):
            return {'message': 'Admin role or creator required'}, 403
        if car.approved and not user.is_admin():
            return {'message': 'For approved object admin role required'}, 403
        # update car
        for key in ('name', 'slug'):
            if args[key]:
                # verify unique
                duplicate = Car.query \
                    .filter(
                        Car.id != args['id'],
                        getattr(Car, key) == args[key]
                    ).first()
                if duplicate:
                    return {'message':
                            'Уже есть автомобиль с данным наименованием'}, 409
                setattr(car, key, args[key])
        # update image
        image = args['image']
        if image:
            try:
                url = upload_image(file_storage=image,
                                   obj_type='car',
                                   obj_id=car.id)
            except Exception as error:
                return {'message': str(error)}, 500
            car.img_src = url

        db.session.commit()
        car_data = car_schema.dump(car)
        return {'status': 'success', 'data': car_data}, 200

    @jwt_required
    def delete(self):
        args = delete_parser.parse_args()
        car = Car.query.filter_by(id=args['id']).first()
        if not car:
            return {'message': 'Car does not found'}, 400
        # check creator or admin
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if not user or (not user.is_admin() and user_id != car.creator_id):
            return {'message': 'Admin role or creator required'}, 403
        # delete car
        db.session.delete(car)
        # delete image
        rm_obj_images(obj_type='car', obj_id=car.id)
        db.session.commit()
        return {}, 204


class CarApproveResourse(Resource):
    @jwt_required
    @roles_required('admin')
    def put(self, id):
        car = Car.query.filter_by(id=id).first()
        if not car:
            return {'message': 'Car does not found'}, 400
        car.approved = not car.approved
        db.session.commit()
        return {}, 204
