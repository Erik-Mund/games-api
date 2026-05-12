from datetime import datetime, timedelta
import jwt
from GameBaseAPI.database import db
from GameBaseAPI.models import User, TokenBlockList
import pytest
from flask_jwt_extended import create_access_token
from GameBaseAPI.tests.get_csrf_token import get_csrf

def test_login_success(client, user):
    response = client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    assert response.status_code == 200

    cookies = response.headers.getlist("Set-Cookie")
    assert any("access_token_cookie" in c for c in cookies)
    assert any("refresh_token_cookie" in c for c in cookies)

def test_protected_route_without_token(client):
    response = client.get("/me")

    assert response.status_code == 401

def test_protected_route_with_token(client, user):
    client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    response = client.get("/me")

    assert response.status_code == 200




def test_expired_token(client, user):
    token = create_access_token(identity=str(user.id), expires_delta=timedelta(seconds=-1))

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


def test_refresh_token(client, user):
    client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    csrf_token = get_csrf(client, is_access=False)

    response = client.post("/refresh", headers={
        "X-CSRF-TOKEN": csrf_token
    })

    assert response.status_code == 200


def test_refresh_token_revocation(client, user):
    client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    csrf_token = get_csrf(client, is_access=False)

    first_response = client.post("/refresh", headers={
        "X-CSRF-TOKEN": csrf_token
    })

    assert first_response.status_code == 200

    cookies = first_response.headers.getlist("Set-Cookie")
    assert any("access_token_cookie" in c for c in cookies)
    assert any("refresh_token_cookie" in c for c in cookies)

    second_response = client.post("/refresh")
    assert second_response.status_code == 401


def test_new_refresh_tokens_work(client, user):
    client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    csrf_token = get_csrf(client, is_access=False)

    first_response = client.post("/refresh", headers={
        "X-CSRF-TOKEN": csrf_token
    })

    assert first_response.status_code == 200

    cookies = first_response.headers.getlist("Set-Cookie")
    assert any("access_token_cookie" in c for c in cookies)
    assert any("refresh_token_cookie" in c for c in cookies)

    csrf_token_2 = get_csrf(client, is_access=False)

    second_response = client.post("/refresh", headers={
        "X-CSRF-TOKEN": csrf_token_2
    })
    assert second_response.status_code == 200

def test_logout_refresh_revokes_token(client, user):
    client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    csrf_token = get_csrf(client, is_access=False)

    client.post("/logout/refresh", headers={
        "X-CSRF-TOKEN": csrf_token
    })

    response = client.post("/refresh", headers={
        "X-CSRF-TOKEN": csrf_token
    })
    assert response.status_code == 401


def test_logouts(client, user, session):
    data = {
        "email": user.email,
        "password": "Password123"
    }
    login = client.post("/login", json=data)
    assert login.status_code == 200

    access_token = get_csrf(client)
    refresh_token = get_csrf(client, is_access=False)

    logout = client.post("/logout", headers={"X-CSRF-TOKEN": access_token})
    assert logout.status_code == 200

    refresh_logout = client.post("/logout/refresh", headers={"X-CSRF-TOKEN": refresh_token})
    assert refresh_logout.status_code == 200

    print(session.query(TokenBlockList).all())

    response = client.get("/me", headers={"X-CSRF-TOKEN": access_token})
    assert response.status_code == 401

    refresh_response = client.post("/refresh", headers={"X-CSRF-TOKEN": refresh_token})
    assert refresh_response.status_code == 401


def test_update_me(client, user):
    data = {
        "email": user.email,
        "password": "Password123"
    }
    client.post("/login", json=data)

    token = get_csrf(client)

    data = {
        "name": "other name",
        "old_password": "Password123",
        "password": "PPassword123"
    }

    response = client.put("/me", json=data, headers={"X-CSRF-TOKEN": token})
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
    client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    token = get_csrf(client)

    data = {
        "name": name,
        "old_password": old_password,
        "password": password
    }

    response = client.put("/me", json=data, headers={"X-CSRF-TOKEN": token})
    assert response.status_code == 400

    body = response.get_json()
    assert "error" in body


def test_me_delete(client, user):
    client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })

    token = get_csrf(client)

    data = {
        "password": "Password123"
    }

    response = client.delete("/me", json=data, headers={"X-CSRF-TOKEN": token})
    assert response.status_code == 204