from datetime import datetime, timedelta
import jwt
from database import db
from models import User, TokenBlockList
import pytest

def test_login_success(client, user):
    response = client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_protected_route_without_token(client):
    response = client.get("/me")

    assert response.status_code == 401

def test_protected_route_with_token(client, user):
    login = client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    token = login.get_json()["access_token"]

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

def test_expired_token(client, user, app):
    payload = {
        "sub": user.id,
        "exp": datetime.utcnow() - timedelta(hours=1)
    }

    expired_token = jwt.encode(
        payload,
        app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401


def test_refresh_token(client, user):
    login = client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    refresh_token = login.get_json()["refresh_token"]

    response = client.post(
        "/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )

    assert response.status_code == 200
    assert "access_token" in response.get_json()


def test_refresh_token_revocation(client, user):
    login = client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    refresh_token = login.get_json()["refresh_token"]

    first_response = client.post(
        "/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )

    assert first_response.status_code == 200
    assert "access_token" and "refresh_token" in first_response.get_json()

    second_response = client.post(
        "/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert second_response.status_code == 401


def test_new_refresh_tokens_work(client, user):
    login = client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    refresh_token = login.get_json()["refresh_token"]

    first_response = client.post(
        "/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )

    assert first_response.status_code == 200
    assert "access_token" and "refresh_token" in first_response.get_json()

    new_refresh_token = first_response.get_json()["refresh_token"]

    second_response = client.post(
        "/refresh",
        headers={"Authorization": f"Bearer {new_refresh_token}"}
    )
    assert second_response.status_code == 200

def test_logout_refresh_revokes_token(client, user):
    login = client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    refresh_token = login.get_json()["refresh_token"]

    client.post("/logout/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    response = client.post("/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert response.status_code == 401


def test_logouts(client, user, session):
    data = {
        "email": user.email,
        "password": "Password123"
    }
    login = client.post("/login", json=data)
    assert login.status_code == 200

    token = login.get_json()["access_token"]
    refresh_token = login.get_json()["refresh_token"]

    logout = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout.status_code == 200

    refresh_logout = client.post("/logout/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert refresh_logout.status_code == 200

    print(session.query(TokenBlockList).all())

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401

    refresh_response = client.post("/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert refresh_response.status_code == 401


def test_update_me(client, user):
    data = {
        "email": user.email,
        "password": "Password123"
    }
    login = client.post("/login", json=data)

    token = login.get_json()["access_token"]

    data = {
        "name": "other name",
        "old_password": "Password123",
        "password": "PPassword123"
    }

    response = client.put("/me", json=data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    this_user = db.session.get(User, user.id)
    assert this_user.name == "other name"
    assert this_user.check_password("PPassword123")


@pytest.mark.parametrize("name, old_password, password", {
    ("", "Password123", "Password123"),
    ("normalname", "PPassword123", "Password123"),
    ("long"*10, "Password123", "Password123"),
    ("normalname","Password123", "password123")
})
def test_invalid_me_inputs(client, user, name, old_password, password):
    login = client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    token = login.get_json()["access_token"]

    data = {
        "name": name,
        "old_password": old_password,
        "password": password
    }

    response = client.put("/me", json=data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400

    body = response.get_json()
    assert "error" in body


def test_me_delete(client, user):
    login = client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    token = login.get_json()["access_token"]

    data = {
        "password": "Password123"
    }

    response = client.delete("/me", json=data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204