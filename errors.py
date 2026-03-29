from flask import jsonify

def register_error_handlers(app):

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({
            "error": "forbidden",
            "message": e.description
        }), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "error": "not found"
        }), 404