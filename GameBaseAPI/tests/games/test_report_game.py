import pytest
from GameBaseAPI.models import Game

@pytest.mark.parametrize("header_fixture, expected_code", [
    ("auth_header", 201),
    ("auth_header_other_user", 201),
    ("auth_header_moderator", 201),
    ("auth_header_admin", 201)
])
def test_report_game_permissions(client, request, expected_code, header_fixture, game):
    header = request.getfixturevalue(header_fixture)

    response = client.post(f"/games/{game.id}/report", headers=header)

    assert response.status_code == expected_code


def test_report_game_successful(client, session, auth_header_admin, game):
    response = client.post(f"/games/{game.id}/report", headers=auth_header_admin)

    assert response.status_code == 201

    reported_game = session.get(Game, game.id)
    assert reported_game.report_count == 1

def test_can_not_report_game_twice(client, session, auth_header_admin, game):
    response = client.post(f"/games/{game.id}/report", headers=auth_header_admin)

    assert response.status_code == 201

    reported_game = session.get(Game, game.id)
    assert reported_game.report_count == 1

    second_response = client.post(f"/games/{game.id}/report", headers=auth_header_admin)

    assert second_response.status_code == 403
    assert reported_game.report_count == 1