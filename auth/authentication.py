import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app, request
from models import User, TokenBlockList
from flask import jsonify, g, render_template
from flask_smorest import Blueprint
from auth.auth_decorators import login_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database import db
from routes.user import check_password
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import limiter
from schemes.auth import *
from schemes.me import *
from flask import current_app
from error_function import error

from flask.views import MethodView

auth_bp = Blueprint("auth", __name__, url_prefix="/", description="Authentication operations")
#me_bp = Blueprint("me", __name__, url_prefix="/me", description="Operations with self")

def generate_token(user):
    payload = {
        "sub": user.id,
        #"role": user.role.value,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }

    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

@auth_bp.get("/login")
@auth_bp.doc(summary="only returns the page, not for Swagger usage")
@limiter.limit("10 per minute")
def get_login():
    return render_template("login.html")

@auth_bp.post("/login")
@auth_bp.arguments(LoginSchema)
@auth_bp.response(200, TokenSchema)
@auth_bp.doc(summary="User login", description="Authenticates users and returns access and refresh JWT tokens")
@limiter.limit("5 per minute")
def login(data):
    #data = request.get_json()
    if not data:
        return error("missing JSON body", 400)

    #email = data.get("email")
    #password = data.get("password")

    email = data["email"]
    password = data["password"]

    if not email or not password:
        current_app.logger.warning("Unsuccessful login attempt")
        return error("missing email or password", 400)

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        current_app.logger.warning("Unsuccessful login attempt")
        return error("Invalid credentials", 401)

    #token = generate_token(user)

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    current_app.logger.info(f"User {user.id} logged in")

    return {"access_token": access_token, "refresh_token": refresh_token}, 200

@auth_bp.post("/refresh")
@auth_bp.doc(summary="token refresh", description="Requires a refresh token. Implements refresh token rotation: blocklists current refresh token, returns a new access token and a new refresh token.")
@limiter.limit("10 per minute")
@jwt_required(refresh=True)
def refresh():
    jwt_data = get_jwt()

    user_id = get_jwt_identity()
    jti = jwt_data["jti"]

    exp_timestamp = jwt_data["exp"]
    expires_at = datetime.fromtimestamp(exp_timestamp)

    old_refresh_token = TokenBlockList(jti=jti, expires_at=expires_at)

    db.session.add(old_refresh_token)
    db.session.commit()

    new_access_token = create_access_token(identity=user_id)
    new_refresh_token = create_refresh_token(identity=user_id)

    return jsonify({"access_token": new_access_token, "refresh_token": new_refresh_token}), 200

@auth_bp.get("/logout")
@auth_bp.doc(summary="only returns the page, not for Swagger usage")
@limiter.limit("10 per minute")
def get_logout():
    return render_template("logout.html")

@auth_bp.post("/logout")
@auth_bp.doc(summary="User logout", description="Revokes the current access token by adding it to the token blocklist. To fully log out, the client also has to call /logout/refresh to revoke the refresh token")
@jwt_required()
def logout():
    jwt_data = get_jwt()
    user = get_jwt_identity()
    jti = jwt_data["jti"]

    exp_timestamp = jwt_data["exp"]
    expires_at = datetime.fromtimestamp(exp_timestamp)

    token = TokenBlockList(jti=jti, expires_at=expires_at)
    db.session.add(token)
    db.session.commit()

    current_app.logger.info(f"User {user} logged out")
    return jsonify({"message":"Successfully logged out"}), 200

@auth_bp.post("/logout/refresh")
@auth_bp.doc(summary="User logout", description="Revokes only the current refresh token by adding it to the token blocklist; for adding current access token to the blocklist use /logout")
@jwt_required(refresh=True)
def logout_refresh():
    jwt_data = get_jwt()
    jti = get_jwt()["jti"]

    exp_timestamp = jwt_data["exp"]
    expires_at = datetime.fromtimestamp(exp_timestamp)

    token = TokenBlockList(jti=jti, expires_at=expires_at)
    db.session.add(token)
    db.session.commit()

    return jsonify({"message": "refresh token revoked"}), 200



