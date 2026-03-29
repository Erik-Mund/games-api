from flask import request, jsonify
from flask_smorest import Blueprint
from database import db
from models import Game, Review
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from routes import paginator
from flask import g
from policies.reviews import *
from policies.authorization import authorize
from auth.auth_decorators import login_required
from extensions import limiter
from flask.views import MethodView
from routes.game import game_bp
from schemes.reviews import *
from flask import current_app
from error_function import error



review_bp = Blueprint("review_bp", __name__, url_prefix="/games/<int:game_id>/reviews", description="operations with reviews")

REVIEW_SORTS = {
    "rating": Review.score,
    "new": Review.updated_at,
    "old": Review.updated_at,
}

def check_score(score):
    if score is None:
        return None, error("score is required", 400)

    if not isinstance(score, int):
        return None, error("score must be an integer", 400)

    try:
        score = int(score)
    except ValueError:
        return None, error("score must be an integer", 400)

    if score < 1 or score > 5:
        return None, error("score must be between 1 and 5", 400)

    return score, None


@game_bp.route('<int:game_id>/reviews')
class ReviewsCollection(MethodView):
    methods = ['GET', 'POST']

    @game_bp.doc(summary="gets all reviews", description="gets, sorts and paginates all reviews per game")
    @limiter.limit("100 per hour")
    def get(self, game_id):
        game = db.session.get(Game, game_id)
        if not game:
            return error("game not found", 404)

        sort = request.args.get("sort", "rating")
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=20, type=int)

        query = Review.query.filter_by(game_id=game_id)
        total_count = query.count()

        try:
            query = paginator.sort_and_paginate(page, per_page, sort, REVIEW_SORTS, query)
        except ValueError as e:
            return error(str(e), 400)

        reviews = query.all()
        return jsonify({"reviews": [review.to_dict() for review in reviews], "total_count": total_count,
                        "count": len(reviews)}), 200

    @game_bp.arguments(PostReviewSchema)
    @game_bp.doc(description="adds a review; game id is necessary")
    @login_required
    @limiter.limit("10 per hour", key_func=lambda: g.current_user)
    def post(self, data, game_id):
        user = g.current_user

        if not data:
            return error("missing JSON body", 400)

        authorize(can_upload_review)

        if "score" not in data:
            current_app.logger.warning("Unsuccessful review post attempt; missing score")
            return error("score is required", 400)

        score, err = check_score(data.get("score"))
        if err:
            return err

        game = db.session.get(Game, game_id)
        if not game:
            current_app.logger.warning("Unsuccessful review post attempt; game not found")
            return error("game not found", 404)
        comment = data.get("comment")

        review = Review(
            score=score,
            game=game,
            user=g.current_user,
            comment=comment
        )
        try:
            game.add_review_incremental(score)
            db.session.add(review)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return error("the game is already reviewed by this user", 400)
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.error("Database error while reviewing a game", exc_info=True)
            return error("Database error", 500)

        current_app.logger.info(f"Review created | user_id={user.id} | score={review.score} | review_id={review.id} | game_id={game_id}")

        return jsonify(review.to_dict()), 201


@game_bp.route('<int:game_id>/reviews/<int:review_id>')
class ReviewResource(MethodView):

    methods = ['GET', 'PUT', 'DELETE']

    @game_bp.doc(summary="gets a review", description="gets a review by id; game id is necessary")
    @limiter.limit("100 per hour")
    def get(self, game_id, review_id):
        review = db.session.get(Review, review_id)
        if not review:
            return error('review not found', 404)
        return jsonify(review.to_dict()), 200

    @game_bp.arguments(PutReviewSchema)
    @game_bp.doc(description="updates a review if authorization is successful")
    @login_required
    @limiter.limit("20 per hour", key_func=lambda: g.current_user)
    def put(self, data, game_id, review_id):
        user = g.current_user

        if not data:
            return error("missing JSON body", 400)

        review = db.session.get(Review, review_id)
        if not review:
            current_app.logger.warning("Unsuccessful review update attempt; review not found")
            return error('review not found', 404)

        authorize(can_update_review, review)

        if "score" not in data:
            return error("score is required", 400)

        score, err = check_score(data.get("score"))
        if err:
            return err

        old_score = review.score
        review.score=score
        if "comment" in data:
            review.comment = data.get("comment")

        try:
            if old_score != score:
                review.game.update_review_incremental(old_score, review.score)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.error("Database error while updating a review", exc_info=True)
            return error("Database error", 500)

        current_app.logger.info(f"Review updated | user_id={user.id} | score={review.score} | review_id={review.id} | game_id={game_id}")

        return jsonify(review.to_dict()), 200


    @game_bp.doc(summary="deletes a review", description="deletes a review if authorizatoin is successful")
    @login_required
    @limiter.limit("20 per hour", key_func=lambda: g.current_user)
    def delete(self, game_id, review_id):
        review = db.session.get(Review, review_id)
        if not review:
            current_app.logger.warning("Unsuccessful review deletion attempt; review not found")
            return error('review not found', 404)

        authorize(can_delete_review, review)

        if g.current_user.id != review.user_id:
            review.user.deleted_reviews += 1

        try:
            review.game.delete_review_incremental(review.score)
            db.session.delete(review)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.error("Database error while deleting a review", exc_info=True)
            return error("database error", 500)

        current_app.logger.info("Review deleted")

        return "", 204
