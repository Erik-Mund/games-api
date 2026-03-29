from models import Review, Game
from database import db

ALLOWED_FIELDS = {
    "score",
    "comment"
}

def make_review(user, game, **kwargs):
    review = Review(user_id=user.id, game_id=game.id **kwargs)

    db.session.add(review)
    db.session.commit()

    return review

def update_review(review, **kwargs):
    for key, value in kwargs.items():
        if key in ALLOWED_FIELDS:
            setattr(review, key, value)

    db.session.commit()
    return review

def delete_review(review):
    db.session.delete(review)
    db.session.commit()
    return True