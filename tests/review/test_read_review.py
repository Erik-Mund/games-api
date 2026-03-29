from models import Review
from datetime import datetime, timedelta

def test_get_reviews_not_found(client, game):
    response = client.get(f"/games/{game.id}/reviews/999999")
    assert response.status_code == 404

def test_get_game_reviews(client, game, review):
    response = client.get(f"/games/{game.id}/reviews")

    assert response.status_code == 200
    body = response.get_json()

    assert isinstance(body, dict)
    assert "reviews" in body
    assert isinstance(body["reviews"], list)

    reviews = body["reviews"]

    assert any(r["id"] == review.id for r in reviews) # any - so at least one of those have to be the fixture one

def test_sort_reviews_by_rating(client, session, game, user, other_user):
    r1 = Review(game_id=game.id, score=4, user_id=user.id)
    session.add(r1)
    session.commit()

    r2 = Review(game_id=game.id, score=5, user_id=other_user.id)
    session.add(r2)
    session.commit()

    response = client.get(f"/games/{game.id}/reviews?sort=rating")

    assert response.status_code == 200
    body = response.get_json()
    reviews = body["reviews"]

    assert reviews[0]["id"] == r2.id
    assert reviews[1]["id"] == r1.id


def test_sort_reviews_by_newest(client, session, game, user, other_user):
    now = datetime.utcnow()

    r1 = Review(game_id=game.id, score=4, user_id=user.id, updated_at=now)
    session.add(r1)
    session.commit()

    r2 = Review(game_id=game.id, score=5, user_id=other_user.id, updated_at=now + timedelta(seconds=1))
    session.add(r2)
    session.commit()

    response = client.get(f"/games/{game.id}/reviews?sort=new")
    assert response.status_code == 200

    body = response.get_json()
    reviews = body["reviews"]

    assert reviews[0]["id"] == r2.id
    assert reviews[1]["id"] == r1.id


def test_sort_reviews_by_oldest(client, session, game, user, other_user):
    now = datetime.utcnow()

    r1 = Review(game_id=game.id, score=4, user_id=user.id, updated_at=now)
    session.add(r1)
    session.commit()

    r2 = Review(game_id=game.id, score=5, user_id=other_user.id, updated_at=now + timedelta(seconds=1))
    session.add(r2)
    session.commit()

    response = client.get(f"/games/{game.id}/reviews?sort=old")
    assert response.status_code == 200

    body = response.get_json()
    reviews = body["reviews"]

    assert reviews[0]["id"] == r1.id
    assert reviews[1]["id"] == r2.id
