from models import Developer_profile
from datetime import datetime, timedelta

def test_get_developer_profile(client, developer_profile):
    response = client.get(f"/developers/{developer_profile.id}")

    assert response.status_code == 200

    body = response.get_json()
    assert body["id"] == developer_profile.id

def test_get_deverloper_profiles_list(client, developer_profile):
    response = client.get("/developers")

    assert response.status_code == 200
    body = response.get_json()

    assert isinstance(body, dict)
    assert "developers" in body
    assert isinstance(body["developers"], list)

    developers = body["developers"]
    assert any(d["id"] == developer_profile.id for d in developers)

def test_get_developer_profiles_not_found(client):
    response = client.get("/developers/999999")
    assert response.status_code == 404

def test_sort_developer_profiles_by_newest(client, session, user, other_user):
    now = datetime.utcnow()

    d1 = Developer_profile(user_id=user.id, studio_name="older", created_at=now)
    session.add(d1)
    session.commit()

    d2 = Developer_profile(user_id=other_user.id, studio_name="newer", created_at=now + timedelta(seconds=1))
    session.add(d2)
    session.commit()

    response = client.get("/developers?sort=new")
    assert response.status_code == 200

    body = response.get_json()
    developers = body["developers"]

    assert developers[0]["id"] == d2.id
    assert developers[1]["id"] == d1.id


def test_sort_developer_profiles_by_oldest(client, session, user, other_user):
    now = datetime.utcnow()
    d1 = Developer_profile(user_id=user.id, studio_name="older", created_at=now)
    session.add(d1)
    session.commit()

    d2 = Developer_profile(user_id=other_user.id, studio_name="newer", created_at=now + timedelta(seconds=1))
    session.add(d2)
    session.commit()

    response = client.get("/developers?sort=old")
    assert response.status_code == 200

    body = response.get_json()
    developers = body["developers"]

    assert developers[0]["id"] == d1.id
    assert developers[1]["id"] == d2.id