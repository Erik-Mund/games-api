from models import Genre
import pytest

@pytest.mark.parametrize("header_fixture, expected_code", [
    ("auth_header", 403),
    ("auth_header_moderator", 201),
    ("auth_header_admin", 201),
    ("auth_header_developer", 403),
])
def test_create_genre_permissions(request, client, header_fixture, expected_code):
    header = request.getfixturevalue(header_fixture)

    data = {
        "name": "Test genre"
    }

    response = client.post("/genres", json=data, headers=header)

    assert response.status_code == expected_code

def test_genre_creation_successful(client, session, auth_header_admin):
    data = {
        "name": "Test Genre"
    }

    created_genre = client.post("/genres", json=data, headers=auth_header_admin)
    assert created_genre.status_code == 201

    body = created_genre.get_json()
    genre_id = body["id"]

    genre = session.get(Genre, genre_id)

    assert genre is not None

    assert genre.name == "Test Genre"


@pytest.mark.parametrize("name, expected_status", [
    ("", 400),
    (None, 422),
    ("   ", 400)
])
def test_create_genre_invalid_inputs(client, name, admin_developer_profile, auth_header_admin, expected_status):
    data = {
        "name":name
    }

    response = client.post("/genres", json=data, headers=auth_header_admin)

    assert response.status_code == expected_status
    assert "error" or "errors" in response.get_json()

def test_create_genre_duplicate(client, admin_developer_profile, auth_header_admin):
    data = {
        "name": "Tested genre"
    }

    first = client.post("/genres", json=data, headers=auth_header_admin)
    assert first.status_code == 201

    response = client.post("/genres", json=data, headers=auth_header_admin)

    assert response.status_code == 400
    assert "error" in response.get_json() or "errors" in response.get_json()

