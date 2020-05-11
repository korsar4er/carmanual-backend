from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    roles = db.Column(db.String(150), nullable=False)
    pass_hash = db.Column(db.String(150))
    creation_date = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    disabled = db.Column(db.Boolean)
    confirmed = db.Column(db.Boolean)

    def __init__(self, name, email, pass_hash):
        self.name = name
        self.email = email
        self.pass_hash = pass_hash
        self.roles = ''
        self.disabled = False
        self.confirmed = False

    def is_admin(self):
        return ('admin' in self.roles.split(','))


class Car(db.Model):
    __tablename__ = 'car'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    img_src = db.Column(db.String(255))
    approved = db.Column(db.Boolean)
    creator_id = db.Column(db.Integer,
                           db.ForeignKey('user.id'),
                           nullable=False)
    creator = db.relationship("User")

    def __init__(self, name, slug, creator_id):
        self.name = name
        self.slug = slug
        self.creator_id = creator_id
        self.approved = False


class Part(db.Model):
    __tablename__ = 'part'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)

    def __init__(self, name, slug):
        self.name = name
        self.slug = slug


class Doc(db.Model):
    __tablename__ = 'doc'
    __table_args__ = (db.UniqueConstraint('slug', 'car_id', 'part_id'), )
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(150), nullable=False, index=True)
    text = db.Column(db.Text)
    approved = db.Column(db.Boolean)
    creator_id = db.Column(db.Integer,
                           db.ForeignKey('user.id'),
                           nullable=False, index=True)
    creator = db.relationship("User")
    car_id = db.Column(db.Integer,
                       db.ForeignKey('car.id', ondelete='CASCADE'),
                       nullable=False, index=True)
    car = db.relationship("Car",
                          backref=db.backref('doc', passive_deletes='all'))
    part_id = db.Column(db.Integer,
                        db.ForeignKey('part.id'),
                        nullable=False, index=True)
    part = db.relationship("Part")

    def __init__(self, name, slug, creator_id, car_id, part_id):
        self.name = name
        self.slug = slug
        self.creator_id = creator_id
        self.car_id = car_id
        self.part_id = part_id
        self.approved = False
