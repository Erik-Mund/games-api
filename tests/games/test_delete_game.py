import pytest
from models import Game

@pytest.mark.parametrize("header_fixture, game_fixture, expected_code", [
    ("auth_header_admin", "game", 204),
    ("auth_header_moderator", "game", 403),
    ("auth_header_moderator", "reported_game", 204),
    ("auth_header_developer", "game", 204),
    ("auth_header_developer", "other_game", 403),
    ("auth_header", "game", 403)
])
def test_delete_game_permissions(client, request, game_fixture, expected_code, header_fixture):
    game = request.getfixturevalue(game_fixture)
    header = request.getfixturevalue(header_fixture)

    response = client.delete(f"/games/{game.id}", headers=header)

    assert response.status_code == expected_code


def test_delete_game_successful(client, session, auth_header_admin, game):
    response = client.delete(f"/games/{game.id}", headers=auth_header_admin)

    assert response.status_code == 204

    deleted_game = session.get(Game, game.id)
    assert deleted_game is None

def test_delete_non_existing_game(client, session, auth_header_admin):
    max_game_id = session.query(Game.id).order_by(Game.id.desc()).first()
    invalid_id = max_game_id[0] + 1 if max_game_id else 1

    response = client.delete(f"/games/{invalid_id}", headers=auth_header_admin)

    assert response.status_code == 404