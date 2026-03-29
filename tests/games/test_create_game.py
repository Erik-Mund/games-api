from models import Game
import pytest

@pytest.mark.parametrize("header_fixture, expected_code", [
    ("auth_header", 403),
    ("auth_header_moderator", 403),
    ("auth_header_admin", 201),
    ("auth_header_developer", 201),
    ("auth_header_reported_developer", 403)
])
def test_create_game_permissions(request, client, developer_profile, admin_developer_profile, header_fixture, expected_code):
    header = request.getfixturevalue(header_fixture)

    data = {
        "title": "Test title",
        #"developer_profile_id": developer_profile.id,
        "price": 2
    }

    response = client.post("/games", json=data, headers=header)

    assert response.status_code == expected_code

def test_game_creation_successful(client, session, auth_header_developer, developer_profile):
    data = {
        "title": "Test Title",
        #"developer_profile_id": developer_profile.id,
        "price": 5,
        "summary": "Test",
        #"genres": ["RPG"] - I'll leave that for later
    }

    created_game = client.post("/games", json=data, headers=auth_header_developer)
    assert created_game.status_code == 201

    body = created_game.get_json()
    game_id = body["id"]

    game = session.get(Game, game_id)

    assert game is not None

    assert game.title == "Test Title"
    assert game.developer_profile_id == developer_profile.id
    assert game.price == 5
    assert game.summary == "Test"


@pytest.mark.parametrize("overrides", [
    {"price":-5},
    {"title":""},
    {"title":None},
    {"title":"   "},
    {"summary":"long"*3000},
    {"title":"long"*300}
])
def test_create_game_invalid_inputs(client, game_data, admin_developer_profile, auth_header_admin, overrides):
    data = game_data(**overrides)

    response = client.post("/games", json=data, headers=auth_header_admin)

    assert response.status_code == 400 or response.status_code == 422
    assert "error" in response.get_json() or "errors" in response.get_json()

def test_create_game_duplicate(client, game_data, admin_developer_profile, auth_header_admin):
    data = game_data()

    first = client.post("/games", json=data, headers=auth_header_admin)
    assert first.status_code == 201

    response = client.post("/games", json=data, headers=auth_header_admin)

    assert response.status_code == 400
    assert "error" in response.get_json()

