from models import Game, Review
from datetime import datetime, timedelta

def test_get_game_success(client, game):
    response = client.get(f"/games/{game.id}")

    assert response.status_code == 200

    body = response.get_json()
    assert body["id"] == game.id
    assert body["title"] == game.title


def test_get_game_not_found(client):
    response = client.get("/games/999999")
    assert response.status_code == 404

def test_get_games_list(client, game):
    response = client.get("/games")

    assert response.status_code == 200
    body = response.get_json()

    assert isinstance(body, dict)
    assert "games" in body
    assert isinstance(body["games"], list)

    games = body["games"]
    assert any(g["id"] == game.id for g in games)


def test_get_games_by_dev(client, game, other_game, developer_profile):
    response = client.get(f"/developers/{developer_profile.id}/games")
    assert response.status_code == 200

    body = response.get_json()
    games = body["games"]

    # Our game must be present
    assert any(g["id"] == game.id for g in games)

    # Other developer's game must NOT be present
    assert not any(g["id"] == other_game.id for g in games)


def test_sort_games_by_newest(client, session, developer_profile):
    now = datetime.utcnow()

    g1 = Game(title="Old", developer_profile_id=developer_profile.id, created_at=now)
    session.add(g1)
    session.commit()

    g2 = Game(title="New", developer_profile_id=developer_profile.id, created_at=now + timedelta(seconds=1))
    session.add(g2)
    session.commit()

    response = client.get("/games?sort=new")
    assert response.status_code == 200

    body = response.get_json()
    games = body["games"]

    assert games[0]["id"] == g2.id
    assert games[1]["id"] == g1.id


def test_sort_games_by_oldest(client, session, developer_profile):
    now = datetime.utcnow()

    g1 = Game(title="Old", developer_profile_id=developer_profile.id, created_at=now)
    session.add(g1)
    session.commit()

    g2 = Game(title="New", developer_profile_id=developer_profile.id, created_at=now + timedelta(seconds=1))
    session.add(g2)
    session.commit()

    response = client.get("/games?sort=old")
    assert response.status_code == 200

    body = response.get_json()
    games = body["games"]

    assert games[0]["id"] == g1.id
    assert games[1]["id"] == g2.id


def test_sort_games_by_rating(client, session, developer_profile):
    g1 = Game(title="Worse", developer_profile_id=developer_profile.id, average_rating=4)
    session.add(g1)
    session.commit()

    g2 = Game(title="Better", developer_profile_id=developer_profile.id, average_rating=5)
    session.add(g2)
    session.commit()

    response = client.get("/games?sort=rating")
    assert response.status_code == 200

    body = response.get_json()
    games = body["games"]
    print(games)

    ids = [g["id"] for g in games]

    assert ids.index(g2.id) < ids.index(g1.id)







