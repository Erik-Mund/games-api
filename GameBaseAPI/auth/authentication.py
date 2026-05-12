import jwt
from datetime import datetime, timedelta, UTC
from GameBaseAPI.models import User, TokenBlockList
from flask import jsonify, render_template
from flask_smorest import Blueprint
from GameBaseAPI.database import db
from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies, \
    unset_access_cookies, unset_refresh_cookies
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from GameBaseAPI.extensions import limiter
from GameBaseAPI.schemes.auth import *
from flask import current_app
from GameBaseAPI.utilities.error_function import error

auth_bp = Blueprint("auth", __name__, url_prefix="/", description="Authentication operations")
#me_bp = Blueprint("me", __name__, url_prefix="/me", description="Operations with self")

def generate_token(user):
    payload = {
        "sub": user.id,
        #"role": user.role.value,
        "exp": lambda: datetime.now(UTC) + timedelta(hours=2)
    }

    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

@auth_bp.get("/login")
@auth_bp.doc(summary="only returns the page, not for Swagger usage")
@limiter.limit("10 per minute")
def get_login():
    return render_template("login.html")

@auth_bp.post("/login")
@auth_bp.arguments(LoginSchema)
@auth_bp.doc(summary="User login, Swagger login below", description="Authenticates users and returns access and refresh JWT tokens")
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

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    response = jsonify({"message": "login successful"})

    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    current_app.logger.info(f"User {user.id} logged in")

    return response, 200

@auth_bp.post("/login-swagger")
@auth_bp.arguments(LoginSchema)
@auth_bp.response(200, TokenSchema)
@auth_bp.doc(summary="User login", description="Authenticates users and returns access and refresh JWT tokens")
@limiter.limit("5 per minute")
def login_swagger(data):
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

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    current_app.logger.info(f"User {user.id} logged in")

    return {"access_token": access_token, "refresh_token": refresh_token}

@auth_bp.post("/refresh")
@auth_bp.doc(summary="token refresh, not intended for Swagger", description="Requires a refresh token. Implements refresh token rotation: blocklists current refresh token, returns a new access token and a new refresh token. This endpoint is intended for browser/client use. Swagger UI does not fully support cookie-based CSRF flow.")
@limiter.limit("10 per minute")
@jwt_required(refresh=True)
def refresh():
    jwt_data = get_jwt()

    user_id = get_jwt_identity()
    jti = jwt_data["jti"]

    existing = TokenBlockList.query.filter_by(jti=jti).first()
    if not existing:
        exp_timestamp = jwt_data["exp"]
        expires_at = datetime.fromtimestamp(exp_timestamp, UTC)

        old_refresh_token = TokenBlockList(jti=jti, expires_at=expires_at)

        db.session.add(old_refresh_token)
        db.session.commit()

    new_access_token = create_access_token(identity=str(user_id))
    new_refresh_token = create_refresh_token(identity=str(user_id))

    response = jsonify({})

    set_access_cookies(response, new_access_token)
    set_refresh_cookies(response, new_refresh_token)

    return response, 200

@auth_bp.post("/logout")
@auth_bp.doc(summary="User logout", description="Revokes the current access token by adding it to the token blocklist. To fully log out, the client also has to call /logout/refresh to revoke the refresh token. This endpoint is intended for browser/client use. Swagger UI does not fully support cookie-based CSRF flow.")
@jwt_required()
def logout():
    jwt_data = get_jwt()
    user = get_jwt_identity()
    jti = jwt_data["jti"]

    existing = TokenBlockList.query.filter_by(jti=jti).first()
    if existing:
        return {"message": "token already revoked"}, 200

    exp_timestamp = jwt_data["exp"]
    expires_at = datetime.fromtimestamp(exp_timestamp, UTC)

    token = TokenBlockList(jti=jti, expires_at=expires_at)
    db.session.add(token)
    db.session.commit()

    response = jsonify({"message":"Successfully logged out"})
    unset_access_cookies(response)

    current_app.logger.info(f"User {user} logged out")
    return response, 200

@auth_bp.post("/logout/refresh")
@auth_bp.doc(summary="User logout", description="Revokes only the current refresh token by adding it to the token blocklist; for adding current access token to the blocklist use /logout. This endpoint is intended for browser/client use. Swagger UI does not fully support cookie-based CSRF flow.")
@jwt_required(refresh=True)
def logout_refresh():
    jwt_data = get_jwt()
    jti = get_jwt()["jti"]

    existing = TokenBlockList.query.filter_by(jti=jti).first()
    if existing:
        return {"message": "token already revoked"}, 200

    exp_timestamp = jwt_data["exp"]
    expires_at = datetime.fromtimestamp(exp_timestamp, UTC)

    token = TokenBlockList(jti=jti, expires_at=expires_at)
    db.session.add(token)
    db.session.commit()

    response = jsonify({"message": "refresh token revoked"})
    unset_refresh_cookies(response)

    return response, 200



