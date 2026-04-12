from flask import jsonify
from sqlalchemy.exc import OperationalError
from error_function import error
from flask import current_app

def register_error_handlers(app):

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({
            "error": "forbidden",
            "message": e.description
        }), 403

    @app.errorhandler(404)
    def not_found(e):
        current_app.logger.error("not found", exc_info=True)
        return error("not found", 404)

    @app.errorhandler(OperationalError)
    def handle_db_error(e):
        current_app.logger.error("Database connection failed", exc_info=True)
        return error("Database connection failed", 503)