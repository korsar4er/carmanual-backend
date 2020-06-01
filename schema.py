from marshmallow import fields, validate
from flask_marshmallow import Marshmallow
from model import User, Car, Part, Doc

ma = Marshmallow()


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = fields.Integer()
    name = fields.String()
    email = fields.String(dump_only=True)
    roles = fields.String()
    creation_date = fields.DateTime(dump_only=True)
    disabled = fields.Boolean()
    confirmed = fields.Boolean(dump_only=True)


class UserRegistrationSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(5))
    email = fields.String(required=True, validate=validate.Email())
    password = fields.String(required=True,
                             validate=validate.Length(6),
                             load_only=True)


class CarSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Car

    id = fields.Integer()
    name = fields.String(required=True)
    slug = fields.String(required=True)
    img_src = fields.String(required=True)
    approved = fields.Boolean()
    creator_id = fields.Integer()
    creator = fields.Nested(UserSchema(only=("id", "name")))


class PartSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Part

    id = fields.Integer()
    name = fields.String(required=True)
    slug = fields.String(required=True)


class DocSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Doc

    id = fields.Integer()
    name = fields.String(required=True)
    slug = fields.String(required=True)
    text = fields.String()
    approved = fields.Boolean(dump_only=True)
    creator_id = fields.Integer()
    creator = fields.Nested(UserSchema(only=("id", "name")), dump_only=True)
    car_id = fields.Integer(required=True)
    car = fields.Nested(CarSchema(only=("id", "name")), dump_only=True)
    part_id = fields.Integer(required=True)
    # part = fields.Nested(PartSchema(only=("id", "name")), dump_only=True)
    part = fields.Nested(PartSchema(), dump_only=True)
