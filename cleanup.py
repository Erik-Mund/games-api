from app import create_app
from database import db
from models import TokenBlockList
from datetime import datetime
from flask import current_app

def cleanup():
    app = create_app()

    with app.app_context():
        now = datetime.utcnow()
        deleted = TokenBlockList.query.filter(TokenBlockList.expires_at < now).delete()

        try:
            db.session.commit()
            current_app.logger.info(f"Deleted {deleted} expired tokens")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Cleanup failed: {e}")

cleanup()