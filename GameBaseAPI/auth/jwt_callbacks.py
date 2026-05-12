from flask_jwt_extended import get_jwt, jwt_manager
from GameBaseAPI.models import TokenBlockList
from GameBaseAPI.app import jwt

from flask import current_app

from GameBaseAPI.database import db
from sqlalchemy import select, exists
from GameBaseAPI.utilities.error_function import error

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]

    token = db.session.query(TokenBlockList).filter_by(jti=jti).first()

    if token:
        current_app.logger.warning("expired token usage attempt")

    return token is not None

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return error("token expired", 401)
