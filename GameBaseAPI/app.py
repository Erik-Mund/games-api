from flask import Flask, render_template

from GameBaseAPI.database import db

from GameBaseAPI.routes import developer, review, game, genre, user, me, html_routes
from GameBaseAPI.utilities.errors import register_error_handlers
from GameBaseAPI.auth import authentication

from GameBaseAPI.extensions import *
import logging

from dotenv import load_dotenv
load_dotenv()

from GameBaseAPI.config import *


import sys



def create_app(config_name=None):

    print("create app started")

    app = Flask(__name__)

    print(sys.version)
    print(sys.executable)






    # Configurations

    if config_name == "testing":
        app.config.from_object(TestingConfig)

    elif config_name == "development":
        app.config.from_object(DevelopmentConfig)

    else:
        app.config.from_object(Config)

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL is not set")
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)

        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
        print(db_url)







    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")



    # Extensions

    print("gets to init")

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app, storage_uri=os.getenv("REDIS_URI"))
    api.init_app(app)

    print("gets through it")

    api.spec.components.security_scheme(
        "BearerAuth",
        {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    )

    # Blueprints

    api.register_blueprint(developer.developer_bp)
    api.register_blueprint(game.game_bp)
    api.register_blueprint(genre.genre_bp)
    api.register_blueprint(authentication.auth_bp)
    api.register_blueprint(user.register_bp)
    api.register_blueprint(me.me_bp)
    api.register_blueprint(html_routes.html_bp)


    # Errors

    register_error_handlers(app)


    @app.route("/")
    def main_page():
        return render_template("index.html")

    return app
