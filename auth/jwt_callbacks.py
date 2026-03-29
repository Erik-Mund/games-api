from flask_jwt_extended import get_jwt, jwt_manager
from models import TokenBlockList
from app import jwt

from flask import current_app

from database import db
from sqlalchemy import select, exists

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]

    token = db.session.query(TokenBlockList).filter_by(jti=jti).first()

    if token:
        current_app.logger.warning("expired token usage attempt")

    return token is not None
