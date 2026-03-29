from models import Game
from database import db

ALLOWED_FIELDS = {
    "title",
    "price",
    "platform",
    "summary",
    "release_year"
}


def make_game(developer_profile, **kwargs):
    game = Game(developer_profile=developer_profile, **kwargs)

    db.session.add(game)
    db.session.commit()

    return game

def update_game(game, **kwargs):

    for key, value in kwargs.items():
        if key in ALLOWED_FIELDS:
            setattr(game, key, value)

    db.session.commit()
    return game

def delete_game(game):
    db.session.delete(game)
    db.session.commit()
