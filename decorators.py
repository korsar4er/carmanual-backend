from functools import wraps
from flask_jwt_extended import get_jwt_identity
from model import User


def is_enabled(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {"message": "User does not found"}, 403
        if user.disabled:
            return {"message": "User is disabled"}, 403
        return f(*args, **kwargs)
    return wrapped


def roles_required(*rolenames):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return {"message": "User does not found"}, 403
            if user.disabled:
                return {"message": "User is disabled"}, 403

            user_set = set(user.roles.split(','))
            required_set = set([str(n) for n in rolenames])
            if not required_set.issubset(user_set):
                return {"message":
                        "Required roles: " + ", ".join(required_set)}, 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


def roles_accepted(*rolenames):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return {"message": "User does not found"}, 403
            if user.disabled:
                return {"message": "User is disabled"}, 403

            user_set = set(user.roles.split(','))
            accepted_set = set([str(n) for n in rolenames])
            if accepted_set.isdisjoint(user_set):
                return {"message":
                        "Accepted roles: " + ", ".join(accepted_set)}, 403
            return f(*args, **kwargs)
        return wrapper
    return decorator
