from flask import request, jsonify
from flask_smorest import Blueprint
from database import db
from models import Game, Developer_profile, Genre
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from routes import paginator
from flask import g
from policies.game import *
from policies.authorization import authorize
from auth.auth_decorators import login_required
from extensions import limiter
from schemes.games import *
from flask import current_app
from error_function import error

game_bp = Blueprint("game_bp", __name__, url_prefix="/games", description="operations with games")

GAME_SORTS = { #all capitals cuz that's how we signal that the variable must not be modified
    "rating": Game.average_rating,
    "new": Game.created_at,
    "old": Game.created_at,
}


@game_bp.get('')
@game_bp.doc(summary="gets all games", description="gets, sorts and paginates all games")
@limiter.limit("100 per hour")
def get_all_games():
    # query params
    sort = request.args.get("sort", "rating")
    #limit = request.args.get("limit", type=int)
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)

    query = Game.query
    total_count = query.count()

    try:
        query = paginator.sort_and_paginate(page, per_page, sort, GAME_SORTS, query)
    except ValueError as e:
        return error(str(e), 400)

    games = query.all()

    return jsonify({"games":[game.to_dict() for game in games], "total_count": total_count, "per_page": per_page, "page": page}), 200

@game_bp.get('<int:game_id>')
@game_bp.doc(description="gets a game by its id")
@limiter.limit("100 per hour")
def get_game(game_id):
    game = db.session.get(Game, game_id)
    if not game:
        return error("game not found", 404)
    return jsonify(game.to_dict()), 200



@game_bp.post('')
@game_bp.arguments(PostGameSchema)
@game_bp.doc(description="requires a name and a developer; price mustn't be negative - 0 is free")
@login_required
@limiter.limit("3 per hour", key_func=lambda: g.current_user)
def add_game(data):
    user = g.current_user

    #data = request.get_json()
    if not data:
        return error("Missing JSON body", 400)

    authorize(can_upload_game)

    # 1. Validate required fields
    title = data.get("title")
    if not title or not title.strip():
        current_app.logger.warning("Unsuccessful game creation attempt; missing title")
        return error("Game title is required", 400)

    if len(title) > 200:
        current_app.logger.warning("Unsuccessful game creation attempt; title too long")
        return error("title too long", 400)

    #developer_profile_id = data.get("developer_profile_id")
    #if not developer_profile_id:
    #    return error("developer id is required", 400)

    # 2. Check if developer exists
    developer = Developer_profile.query.filter_by(user_id=g.current_user.id).first()
    if not developer:
        current_app.logger.warning("Unsuccessful game creation attempt; missing developer profile")
        return error("Developer not found", 404)
    developer_profile_id = developer.id

    # 3. Optional fields
    release_year = data.get("release_year")
    summary = data.get("summary")
    platform = data.get("platform")
    price = data.get("price", 0)  # default to 0 if not provided

    if not isinstance(price, int) or price < 0:
        current_app.logger.warning("Unsuccessful game creation attempt; invalid price input")
        return error("invalid price input", 400)

    if summary is not None:
        if len(summary) > 5000:
            current_app.logger.warning("Unsuccessful game creation attempt; summary too long")
            return error("summary too long", 400)

    # 4. Handle genres (many-to-many)
    genre_names = data.get("genres", [])
    genres = []
    for name in genre_names:
        genre = db.session.query(Genre).filter_by(name=name).first()
        if genre:
            genre.game_count += 1
            genres.append(genre)
        else:
            current_app.logger.warning("Unsuccessful game creation attempt; genre(s) not found")
            return error(f"Genre {name} not found", 404)

    # 5. Create the Game object
    game = Game(
        title=title,
        developer_profile=developer,  # assign the developer object,
        developer_profile_id=developer_profile_id,
        release_year=release_year,
        summary=summary,
        platform=platform,
        price=price,
        genres=genres,  # assign the list of genre objects for the many-to-many relationship
    )

    # 6. Commit to database
    try:
        db.session.add(game)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        current_app.logger.warning("Unsuccessful game creation attempt; duplicate title")
        return error("Developer already has a game with this title", 400)
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.error("Database error while creating a game", exc_info=True)
        return error("Database error", 500)

    current_app.logger.info(f"Game created | user_id={user.id} | title={title} | game_id={game.id}")

    # 7. Return the created game
    return jsonify(game.to_dict()), 201


@game_bp.put('<int:game_id>')
@game_bp.arguments(PutGameSchema)
@login_required
@limiter.limit("3 per hour", key_func=lambda: g.current_user)
def update_game(data, game_id):
    user = g.current_user

    game = db.session.get(Game, game_id)
    if not game:
        return error("game not found", 404)

    if not data:
        return error("Missing JSON body", 400)

    authorize(can_update_game, game)

    # Update title if provided
    if "title" in data:
        if not data["title"] or not data["title"].strip():
            current_app.logger.warning("Unsuccessful game update attempt; missing title")
            return error("Game title cannot be empty", 400)
        game.title = data["title"]

    # Update developer if provided
    if "developer_profile" in data:
        current_app.logger.warning("Unsuccessful game update attempt; developer can't be updated")
        return error("developer can not be updated", 400)

    optional_fields = ["release_year", "summary", "platform", "price"]

    for field in optional_fields:
        if field in data:
            value = data[field]

            if field == "price":
                try:
                    value = int(value)
                except (TypeError, ValueError):
                    current_app.logger.warning("Unsuccessful game creation attempt; invalid price input")
                    return error("invalid price input", 400)

                if value < 0:
                    current_app.logger.warning("Unsuccessful game creation attempt; invalid price input")
                    return error("invalid price input", 400)

            setattr(game, field, value)

    # Update genres only if provided
    if "genres" in data:
        genre_names = data["genres"]
        genres = []

        for name in genre_names:
            genre = db.session.query(Genre).filter_by(name=name).first()
            if not genre:
                current_app.logger.warning("Unsuccessful game creation attempt; genre(s) not found")
                return error(f"Genre '{name}' not found", 404)

            genres.append(genre)

        old_set = set(game.genres)
        new_set = set(genres)

        for genre in old_set - new_set:
            genre.game_count -= 1

        for genre in new_set - old_set:
            genre.game_count += 1

        game.genres = genres


    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        current_app.logger.warning("Unsuccessful game creation attempt; duplicate title")
        return error("Developer already has a game with this title", 400)
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.error("Database error while updating a game", exc_info=True)
        return error("Database error", 500)

    current_app.logger.info(f"Game updated | user_id={user.id} | title={game.title} | game_id={game.id}")

    return jsonify({
        "message": "Game successfully updated",
        "game": game.to_dict()
    }), 200


@game_bp.delete('<int:game_id>')
@game_bp.doc(description="deletes a game by its id")
@login_required
def delete_game(game_id):
    user = g.current_user

    game = db.session.get(Game, game_id)
    if not game:
        current_app.logger.warning("Unsuccessful game deletion attempt; game not found")
        return error("game not found", 404)

    authorize(can_delete_game, game)

    if game.genres is not None:
        for genre in game.genres:
            genre.game_count -= 1

    if user.id != game.developer_profile.user_id:
        game.developer_profile.user.deleted_games += 1

    try:
        db.session.delete(game)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.error("Database error while deleting a game", exc_info=True)
        return error("database error", 500)

    current_app.logger.info("Game deleted")

    return "", 204

