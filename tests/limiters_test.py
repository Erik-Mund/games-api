from models import UserRole

def test_login_limiter(client, user):
    data = {
        "email": user.email,
        "password": "WrongPassword123"
    }

    for i in range(5):
        client.post("/login", json=data)

    response = client.post("/login", json=data)
    assert response.status_code == 429

def test_register_limiter(client):
    data = {
        "email": "test@email.com",
        "name": "normal_username",
        "password": "Password123"
    }

    for i in range(3):
        client.post("/register", json=data)

    response = client.post("/register", json=data)
    assert response.status_code == 429

def test_get_me_limiter(client, user):
    data = {
        "email": user.email,
        "password": "Password123"
    }
    login = client.post("/login", json=data)
    assert login.status_code == 200

    token = login.get_json()["access_token"]

    for i in range(100):
        client.get("/me", headers={"Authorization": f"Bearer {token}"})

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 429