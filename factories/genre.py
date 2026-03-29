from models import Genre
from database import db

def make_genre(name):
    existing = Genre.query.filter_by(name=name).first()
    if existing:
        return existing

    genre = Genre(name=name)

    db.session.add(genre)
    db.session.commit()

    return genre

def delete_genre(genre):
    db.session.delete(genre)
    db.session.commit()

    return True