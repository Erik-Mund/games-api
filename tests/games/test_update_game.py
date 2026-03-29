import pytest
from models import Game

@pytest.mark.parametrize("header_fixture, game_fixture, expected_status",
                         [("auth_header_admin", "game", 200),
                          ("auth_header_developer", "game", 200),
                          ("auth_header_developer", "other_game", 403),
                          ("auth_header_moderator", "game", 403),
                          ("auth_header", "game", 403)])
def test_update_game_permissions(request, session, client, header_fixture, game_fixture, expected_status):
    headers = request.getfixturevalue(header_fixture) # gets the fixture
    game = request.getfixturevalue(game_fixture)

    data = {
        "title": "Test Title updated"
    }

    response = client.put(f"/games/{game.id}", json=data, headers=headers)

    assert response.status_code == expected_status
    if expected_status == 403:
        assert session.get(Game, game.id).title != "Test Title updated"

def test_update_game_successful(client, session, game, auth_header_admin):
    data = {
        "title": "Admin Title",
    }

    client.put(f"/games/{game.id}", json=data, headers=auth_header_admin)

    updated = session.get(Game, game.id)
    assert updated.title == "Admin Title"

def test_invalid_price_input_rejected(client, game, auth_header_admin):
    data = {
        "price": -1
    }

    response = client.put(f"/games/{game.id}", json=data, headers=auth_header_admin)

    assert response.status_code == 400

    body = response.get_json()
    assert "error" in body

def test_invalid_title_input_rejected(client, game, auth_header_admin):
    data = {
        "title": ""
    }

    response = client.put(f"/games/{game.id}", json=data, headers=auth_header_admin)

    assert response.status_code == 400

    body = response.get_json()
    assert "error" in body


def test_update_non_existing_game(client, session, admin_developer_profile, auth_header_admin):
    max_game_id = session.query(Game.id).order_by(Game.id.desc()).first()
    invalid_game_id = (max_game_id[0] + 1) if max_game_id else 1

    data = {
        "title": "Updated title"
    }

    response = client.put(f"/games/{invalid_game_id}", json=data, headers=auth_header_admin)

    assert response.status_code == 404


