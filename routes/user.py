from models import User, UserRole
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask import g, jsonify, request, current_app
from flask_smorest import Blueprint
from database import db
from extensions import limiter
from schemes.auth import RegisterSchema
from error_function import error

register_bp = Blueprint("register_bp", __name__)

def check_password(password):
    password = str(password)
    if len(password) < 8:
        raise ValueError("password must be at least 8 characters long")
    if not any(c.isdigit() for c in password):
        raise ValueError("password must contain at least 1 integer")
    if not any(c.islower() for c in password):
        raise ValueError("password must contain at least 1 lowercase letter")
    if not any(c.isupper() for c in password):
        raise ValueError("password must contain at least 1 capital letter")


@register_bp.route("/register", methods=['POST'])
@register_bp.arguments(RegisterSchema)
@register_bp.doc(summary="creates a user", description="requires proper name, password and an email; name and email must be unique")
@limiter.limit("3 per minute; 30 per hour")
def register(data):
    #data = request.get_json()
    if not data:
        return error("missing JSON body", 400)

    required_fields = ["name", "password", "email"]
    for field in required_fields:
        if not data.get(field):
            current_app.logger.warning("Unsuccessful registration attempt; missing required fields")
            return error(f"{field} is required", 400)

    if len(data["name"]) > 30:
        current_app.logger.warning("Unsuccessful registration attempt; name is too long")
        return error("name too long", 400)

    if "@" not in data["email"] or "." not in data["email"]:
        current_app.logger.warning("Unsuccessful registration attempt; invalid email")
        return error("invalid email", 400)

    if User.query.filter_by(name=data["name"]).first():
        current_app.logger.warning("Unsuccessful registration attempt; name is already taken")
        return error("user with this name already exists", 400)

    if User.query.filter_by(email=data["email"]).first():
        current_app.logger.warning("Registration failed; email is already taken")
        return error("user with this email already exists", 400)

    try:
        check_password(data["password"])
    except ValueError as e:
        current_app.logger.warning("Unsuccessful registration attempt; password is too weak")
        return error(str(e), 400)

    user = User(
        name=data["name"],
        email=data["email"],
        role=UserRole.USER
    )
    user.set_password(data["password"])

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        current_app.logger.warning("Unsuccessful registration attempt; unique constrain failed")
        return error("unique constraint failed")
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error("Database error while registration", exc_info=True)
        return error("Database error", 500)

    current_app.logger.info(f"Account created | user_id={user.id} | name={user.name} | email={user.email}")

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value
    }, 201





