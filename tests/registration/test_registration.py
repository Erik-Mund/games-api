import pytest
from models import User, UserRole

def test_registration_success(client, session):
    data = {
        "name": "test user",
        "email": "test_email@email.com",
        "password": "Password123"
    }

    response = client.post("/register", json=data)
    assert response.status_code == 201

    body = response.get_json()
    user_id = body["id"]

    user = session.get(User, user_id)

    assert user is not None

    assert user.name == data["name"]
    assert user.email == data["email"]

@pytest.mark.parametrize("name, password, email, expected_status", [
    ("n"*31, "Password123", "test@email.com", 400),
    ("normal_name", "badpassword", "test@email.com", 400),
    ("normal_name", "Password123", "invalidemail", 422),
    ("", "Password123", "test@email.com", 400),
    (None, "Password123", "test@email.com", 422),
    ("normal_name", "password123", "test@email.com", 400),
    ("normal_name", "123456789A", "test@email.com", 400),
    ("normal_name", "pswd", "test@email.com", 422),
])
def test_user_invalid_inputs(name, password, email, client, expected_status):
    data = {
        "name": name,
        "password": password,
        "email": email
    }

    response = client.post("/register", json=data)
    assert response.status_code == expected_status
    assert "error" in response.get_json() or "errors" in response.get_json()

def test_user_duplicates(client):
    data = {
        "name": "basic_name",
        "password": "Password123",
        "email": "test@email.com"
    }

    first = client.post("/register", json=data)
    assert first.status_code == 201

    duplicate = client.post("/register", json=data)
    assert duplicate.status_code == 400
    assert "error" in duplicate.get_json()