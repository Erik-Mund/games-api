from flask import request
from GameBaseAPI.database import db
from GameBaseAPI.models import User
from GameBaseAPI.utilities.error_function import error


from functools import wraps
from flask import g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):

        if request.headers.get("Authorization"):
            verify_jwt_in_request(locations=["headers"])
        else:
            verify_jwt_in_request(locations=["cookies"])

        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)

        if not user:
            return error("user not found", 404)

        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper


def optional_login(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            if request.headers.get("Authorization"):
                verify_jwt_in_request(optional=True, locations=["headers"])
            else:
                verify_jwt_in_request(optional=True, locations=["cookies"])

            user_id = get_jwt_identity()
            if user_id:
                g.current_user = db.session.get(User, user_id)
            else:
                g.current_user = None
        except:
            g.current_user = None

        return fn(*args, **kwargs)

    return wrapper
