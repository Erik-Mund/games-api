from models import User
from flask import jsonify, g, current_app
from flask_smorest import Blueprint
from auth.auth_decorators import login_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database import db
from routes.user import check_password
from flask_jwt_extended import get_jwt_identity
from extensions import limiter
from schemes.me import *

from flask.views import MethodView
from error_function import error

me_bp = Blueprint("me", __name__, url_prefix="/me", description="Operations with self")

@me_bp.route("")
class CurrentUser(MethodView):

    decorators = [login_required]
    methods = ['GET', 'PUT', 'DELETE']

    @me_bp.doc(summary="get current user")
    @limiter.limit("100 per hour", key_func=lambda: str(get_jwt_identity() or "anon"))
    def get(self):
        return {
            "id": g.current_user.id,
            "name": g.current_user.name,
            "email": g.current_user.email,
            "role": g.current_user.role.value
        }, 200

    @me_bp.arguments(PutMeSchema)
    @me_bp.doc(summary="update current user")
    def put(self, data):
        user = db.session.get(User, g.current_user.id)
        if not user:
            current_app.logger.warning("Unsuccessful self update attempt; user not found")
            return error("user not found", 404)

        #data = request.get_json()
        if not data:
            return error("missing JSON body")

        if "name" in data:
            if not data.get("name"):
                current_app.logger.warning("Unsuccessful self update attempt; invalid name input")
                return error("invalid name input")
            if len(data["name"]) > 30:
                current_app.logger.warning("Unsuccessful self update attempt; name too long")
                return error("name too long")

            user.name = data["name"]

        if "password" in data:
            if not data.get("old_password"):
                current_app.logger.warning("Unsuccessful self update attempt; missing password")
                return error("old password required")

            if user.check_password(data["old_password"]):
                try:
                    check_password(data["password"]) # imported function from the user route
                except ValueError as e:
                    current_app.logger.warning("Unsuccessful self update attempt; new password is too weak")
                    return error(str(e), 400)

                user.set_password(data["password"])

            else:
                return error("old password is incorrect")

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            current_app.logger.warning("Unsuccessful self update attempt; name already taken")
            return error("name already taken", 400)
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.error("Database error while updating self", exc_info=True)
            return error("Database error", 500)

        current_app.logger.info(f"Self updated | user_id={user.id} | name={user.name} | email={user.email}")

        return {
            "name": user.name,
            "role": user.role.value,
            "email": user.email
        }, 200

    @me_bp.arguments(DeleteMeSchema)
    @me_bp.doc(summary="delete current user")
    def delete(self, data):
        user = db.session.get(User, g.current_user.id)
        if not user:
            current_app.logger.warning("Unsuccessful self deletion attempt; user not found")
            return error("user not found", 404)

        #data = request.get_json()
        if not user.check_password(data.get("password")):
            current_app.logger.warning("Unsuccessful self deletion attempt; invalid password")
            return error("invalid password")

        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.error("Database error while self deletion", exc_info=True)
            return error("Database error", 500)

        current_app.logger.info("Self deleted")

        return "", 204