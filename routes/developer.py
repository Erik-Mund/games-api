from flask import request, jsonify
from flask_smorest import Blueprint
from database import db
from models import Developer_profile, Game
from routes.game import GAME_SORTS
from sqlalchemy.exc import SQLAlchemyError
from routes import paginator
from flask import g
from policies.developers import *
from policies.authorization import authorize
from auth.auth_decorators import login_required
from extensions import limiter
from flask.views import MethodView
from schemes.developers import *
from error_function import error
from flask import current_app

#user = g.current_user

developer_bp = Blueprint("developer_bp", __name__, url_prefix="/developers", description="operations with developers")

DEVELOPER_SORTS = {
    "new": Developer_profile.created_at,
    "old": Developer_profile.created_at,
}


@developer_bp.route('')
class DevelopersCollection(MethodView):

    methods = ['GET', 'POST']

    @developer_bp.doc(summary="gets all developers", description="gets, sorts and paginates all developers")
    @limiter.limit("100 per hour")
    def get(self):

        # query params
        sort = request.args.get("sort", "new")
        #limit = request.args.get("limit", type=int)
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=20, type=int)

        query = Developer_profile.query
        total_count = query.count()

        try:
            query = paginator.sort_and_paginate(page, per_page, sort, DEVELOPER_SORTS, query)
        except ValueError as e:
            return error(str(e), 400)

        developers = query.all()
        return jsonify({"developers": [dev.to_dict() for dev in developers], "total_count": total_count, "count":len(developers)}), 200

    @developer_bp.arguments(PostDeveloperSchema)
    @developer_bp.doc(description="checks authorization and posts a developer" , security=[{"BearerAuth": []}])
    @login_required
    def post(self, data):
        user = g.current_user

        if not data:
            return error("missing JSON body", 400)

        studio_name = data.get("studio_name")
        if not studio_name or not studio_name.strip():
            current_app.logger.warning("unsuccessful developer creation attempt; studio name field missing")
            return error("Studio name is required", 400)


        #allowed, reason = can_create_developer(g.current_uesr)
        #if not allowed:
        #    return error(reason, 403)

        authorize(can_create_developer)

        developer_profile = Developer_profile(studio_name=studio_name, user_id=g.current_user.id)

        try:
            db.session.add(developer_profile)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return error(f"database error: {str(e)}", 500)

        current_app.logger.info(f"Developer profile created | user_id={user.id} | studio_name={studio_name} | developer_profile_id={developer_profile.id}")

        return jsonify({
            "message": "developer profile created successfully",
            "developer_profile": developer_profile.to_dict(),
            "id":developer_profile.id
        }), 201


@developer_bp.route('<int:dev_id>')
class DeveloperResource(MethodView):

    methods = ['GET', 'PUT', 'DELETE']

    @developer_bp.doc(description="gets a developer by its id")
    @limiter.limit("100 per hour")
    def get(self, dev_id):
        developer = db.session.get(Developer_profile, dev_id)
        if developer is None:
            return error("developer not found", 404)
        return jsonify(developer.to_dict()), 200

    @developer_bp.arguments(PutDeveloperSchema)
    @login_required
    @limiter.limit("3 per hour", key_func=lambda: g.current_user)
    def put(self, data, dev_id):
        user = g.current_user

        if not data:
            return error("missing JSON body", 400)

        developer_profile = db.session.get(Developer_profile, dev_id)
        if developer_profile is None:
            return error("developer not found", 404)

        studio_name = data.get("studio_name")
        if not studio_name or not studio_name.strip():
            return error("Studio name is required", 400)

        if len(studio_name) > 150:
            return error("studio name too long")

        # allowed, reason = can_update_developer(g.current_uesr, developer_profile)
        # if not allowed:
        #    return error(reason, 403)

        authorize(can_update_developer, developer_profile)

        developer_profile.studio_name = studio_name

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.warning("database error while creating a developer profile", exc_info=True)
            return error("database error", 500)

        current_app.logger.info(f"Developer profile updated | user_id={user.id} | studio_name={studio_name} | developer_profile_id={developer_profile.id}")

        return jsonify({
            "message": "developer profile updated successfully",
            "developer_profile": developer_profile.to_dict()
        }), 200

    @developer_bp.doc(description="deletes a developer by its id")
    @login_required
    def delete(self, dev_id):
        developer_profile = db.session.get(Developer_profile, dev_id)
        if developer_profile is None:
            return error("developer not found", 404)

        authorize(can_delete_developer, developer_profile)

        try:
            db.session.delete(developer_profile)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.warning("database errors while deleting a developer profile", exc_info=True)
            return error("database error", 500)

        current_app.logger.info("Developer profile deleted")

        return "", 204



@developer_bp.get('<int:developer_profile_id>/games')
@developer_bp.doc(description="gets games by its developer's id")
@limiter.limit("100 per hour")
def get_games_by_developer(developer_profile_id):
    developer = db.session.get(Developer_profile, developer_profile_id)
    if not developer:
        return error("developer not found", 404)

    # query params
    sort = request.args.get("sort", "rating")
    #limit = request.args.get("limit", type=int)
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)

    query = Game.query.filter_by(developer_profile_id=developer_profile_id)
    total_count = query.count()

    try:
        query = paginator.sort_and_paginate(page, per_page, sort, GAME_SORTS, query)
    except ValueError as e:
        return error(str(e), 400)

    games = query.all()

    return jsonify({"developer":developer.studio_name, "games":[game.to_dict() for game in games], "total_count": total_count, "per_page": per_page, "page": page}), 200


