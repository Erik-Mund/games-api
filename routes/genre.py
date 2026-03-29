from flask import request, jsonify
from flask_smorest import Blueprint
from database import db
from models import Genre, Game
from routes.game import GAME_SORTS
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from routes import paginator
from policies.genres import *
from policies.authorization import authorize
from auth.auth_decorators import login_required
from extensions import limiter
from flask.views import MethodView
from schemes.genres import *
from error_function import error
from flask import current_app, g


genre_bp = Blueprint("genre_bp", __name__, url_prefix="/genres", description="operations with genres")

GENRE_SORTS = {
    "new": Genre.created_at,
    "old": Genre.created_at
}


@genre_bp.route('')
class GenresCollection(MethodView):

    methods = ['GET', 'POST']

    @genre_bp.doc(summary="gets all genres", description="gets, sorts and paginates all genres")
    @limiter.limit("100 per hour")
    def get(self):
        sort = request.args.get("sort", "new")
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=20, type=int)

        query = Genre.query
        total_count = query.count()

        try:
            query = paginator.sort_and_paginate(page, per_page, sort, GENRE_SORTS, query)
        except ValueError as e:
            return error(str(e), 400)

        genres = query.all()
        return jsonify({"genres":[gr.to_dict() for gr in genres], "total_count": total_count, "count":len(genres)}), 200

    @genre_bp.arguments(PostGenreSchema)
    @login_required
    def post(self, data):
        user = g.current_user
        if not data:
            return error("missing JSON body", 400)

        authorize(can_upload_genres)

        name = data.get("name")
        if not name or not name.strip():
            current_app.logger.warning("Unsuccessful genre creation attempt; genre name missing")
            return error("genre name is required", 400)

        if len(name) > 100:
            current_app.logger.warning("Unsuccessful genre creation attempt; genre name too long")
            return error("genre name too long", 400)

        genre = Genre(name=name)

        try:
            db.session.add(genre)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return error("Genre with this title already exists", 400)
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.error("Database error while genre creation", exc_info=True)
            return error("database error", 500)

        current_app.logger.info(f"Genre created | user_id={user.id} | genre_id={genre.id} | genre name={genre.name}")

        return jsonify(genre.to_dict()), 201

@genre_bp.route('<int:gr_id>')
class GenreResource(MethodView):

    methods = ['GET', 'DELETE']

    @genre_bp.doc(description="gets a genre by its id")
    @limiter.limit("100 per hour")
    def get(self, gr_id):
        genre = db.session.get(Genre, gr_id)
        if genre is None:
            return error("genre not found", 404)
        return jsonify(genre.to_dict()), 200

    @genre_bp.doc(description="deletes a genre by its id")
    @login_required
    def delete(self, gr_id):
        genre = db.session.get(Genre, gr_id)
        if genre is None:
            current_app.logger.warning("Unsuccessful genre deletion attempt; genre not found")
            return error("genre not found", 404)

        authorize(can_delete_genres, genre)

        try:
            db.session.delete(genre)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.error("Database error", exc_info=True)
            return error("database error", 500)

        current_app.logger.info("Genre deleted")

        return "", 204


@genre_bp.doc(description="gets a game by its genre's id")
@genre_bp.route('<int:genre_id>/games', methods=['GET'])
@limiter.limit("100 per hour")
def get_games_by_genre(genre_id):
    genre = db.session.get(Genre, genre_id)
    if not genre:
        return error("genre not found", 404)

    # query params
    sort = request.args.get("sort", "rating")
    #limit = request.args.get("limit", type=int)
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)

    #limit = min(limit, 100)

    query = (
        Game.query.join(Game.genres).filter(Genre.id == genre_id)
    )
    total_count = query.count()

    try:
        query = paginator.sort_and_paginate(page, per_page, sort, GAME_SORTS, query)
    except ValueError as e:
        return error(str(e), 400)


    games = query.all()
    return jsonify({"genre": genre.name, "games":[game.to_dict() for game in games], "total_count": total_count, "per_page": per_page, "page": page}), 200