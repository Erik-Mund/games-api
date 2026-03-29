import jwt
from functools import wraps
from flask import request, g, current_app, jsonify
from database import db
from models import User
from error_function import error


from functools import wraps
from flask import g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import current_app

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):

        verify_jwt_in_request()  # validates token + blocklist

        user_id = get_jwt_identity()

        user = db.session.get(User, user_id)
        if not user:
            current_app.logger.warning(f"JWT valid but user {user.id} not found")
            return error("user not found", 404)

        g.current_user = user

        return fn(*args, **kwargs)

    return wrapper
