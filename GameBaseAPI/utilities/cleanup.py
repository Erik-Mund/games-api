from GameBaseAPI.app import create_app
from GameBaseAPI.database import db
from GameBaseAPI.models import TokenBlockList
from datetime import datetime, UTC
from flask import current_app

def cleanup():
    app = create_app()

    with app.app_context():
        now = lambda: datetime.now(UTC)
        deleted = TokenBlockList.query.filter(TokenBlockList.expires_at < now).delete()

        try:
            db.session.commit()
            current_app.logger.info(f"Deleted {deleted} expired tokens")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Cleanup failed: {e}")
