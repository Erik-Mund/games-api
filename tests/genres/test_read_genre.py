from models import Genre
from datetime import datetime, timedelta

def test_get_genre(client, genre):
    response = client.get(f"/genres/{genre.id}")

    assert response.status_code == 200

    body = response.get_json()
    assert body["id"] == genre.id

def test_get_genres_list(client, genre):
    response = client.get("/genres")

    assert response.status_code == 200
    body = response.get_json()

    assert isinstance(body, dict)
    assert "genres" in body
    assert isinstance(body["genres"], list)

    genres = body["genres"]
    assert any(g["id"] == genre.id for g in genres)

def test_get_genre_not_found(client):
    response = client.get("/genres/999999")
    assert response.status_code == 404


def test_sort_genres_by_newest(client, session, user, developer_profile):
    now = datetime.utcnow()

    g1 = Genre(name="older", created_at=now)
    session.add(g1)
    session.commit()

    g2 = Genre(name="newer", created_at=now + timedelta(seconds=1))
    session.add(g2)
    session.commit()

    response = client.get("/genres?sort=new")
    assert response.status_code == 200

    body = response.get_json()
    genres = body["genres"]

    assert genres[0]["id"] == g2.id
    assert genres[1]["id"] == g1.id


def test_sort_genres_by_oldest(client, session, user, developer_profile):
    now = datetime.utcnow()

    g1 = Genre(name="older", created_at=now)
    session.add(g1)
    session.commit()

    g2 = Genre(name="newer", created_at=now + timedelta(seconds=1))
    session.add(g2)
    session.commit()

    response = client.get("/genres?sort=old")
    assert response.status_code == 200

    body = response.get_json()
    genres = body["genres"]

    assert genres[0]["id"] == g1.id
    assert genres[1]["id"] == g2.id