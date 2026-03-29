from flask import Flask, render_template
from flask_smorest import Api

from database import db

from routes import developer, game, review, genre, user, me
from errors import register_error_handlers
from auth import authentication

from datetime import timedelta

from extensions import *
import logging

import os



def create_app(config_name=None):

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")




    # -------------------------
    # Config
    # -------------------------

    if config_name == "testing":
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["RATELIMIT_STORAGE_URI"] = "memory://"
    elif config_name == "development":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///games.db"
    else:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL is not set")

        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)

        app.config["SQLALCHEMY_DATABASE_URI"] = db_url

    app.config["API_TITLE"] = "The Game Shop"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/api"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    app.config["DEBUG"] = config_name == "development"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    app.config["OPENAPI_SWAGGER_UI_CONFIG"] = {"docExpansion": "full"}

    app.config["API_SPEC_OPTIONS"] = {
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        },
        "security": [{"BearerAuth": []}]
    }

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


    # -------------------------
    # Extensions
    # -------------------------

    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    api.init_app(app)

    api.spec.components.security_scheme(
        "BearerAuth",
        {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    )

    import auth.jwt_callbacks


    # -------------------------
    # Blueprints
    # -------------------------

    api.register_blueprint(developer.developer_bp)
    api.register_blueprint(game.game_bp)
    api.register_blueprint(review.review_bp)
    api.register_blueprint(genre.genre_bp)
    api.register_blueprint(authentication.auth_bp)
    api.register_blueprint(user.register_bp)
    api.register_blueprint(me.me_bp)


    # Errors


    register_error_handlers(app)



    # Auth Mock


    #@app.before_request
    #def load_user():
    #    user_id = request.headers.get("X-User-Id")
#
    #    if user_id:
   #         g.current_user = db.session.get(User, user_id)
   #     else:
    #        g.current_user = None


    with app.app_context():
        db.create_all()
    # Routes


    @app.route("/")
    def hello_world():
        return render_template("index.html")

    return app
