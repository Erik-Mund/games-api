from models import Review
import pytest

@pytest.mark.parametrize("header_fixture, expected_code", [
    ("auth_header", 201),
    ("auth_header_reported_user", 403),
    ("auth_header_moderator", 201),
    ("auth_header_admin", 201),
    ("auth_header_developer", 201)
])
def test_create_review_permissions(request, client, game, header_fixture, expected_code):
    header = request.getfixturevalue(header_fixture)

    data = {
        "score": 5,
        "comment": "Test comment"
    }

    response = client.post(f"/games/{game.id}/reviews", json=data, headers=header)

    assert response.status_code == expected_code

def test_review_creation_successful(client, session, auth_header_admin, game):
    data = {
        "score": 5,
        "comment": "Test comment"
    }

    created_review = client.post(f"/games/{game.id}/reviews", json=data, headers=auth_header_admin)
    assert created_review.status_code == 201

    body = created_review.get_json()
    review_id = body["id"]

    review = session.get(Review, review_id)

    assert review is not None

    assert review.score == 5
    assert review.comment == "Test comment"


def test_create_review_duplicate_rejected(client, auth_header_other_user, game):
    data = {
        "score": 5,
    }

    first = client.post(f"/games/{game.id}/reviews", json=data, headers=auth_header_other_user)
    assert first.status_code == 201

    response = client.post(f"/games/{game.id}/reviews", json=data, headers=auth_header_other_user)

    assert response.status_code == 400

    body = response.get_json()
    assert "error" in body


@pytest.mark.parametrize("data", [
    {"score": -1},
    {"score": None},
    {"score": 6},
    {"score": 4.5},
    {"comment": "long"*500}
])
def test_create_review_invalid_inputs(client, auth_header_admin, game, data):
    response = client.post(f"/games/{game.id}/reviews", json=data, headers=auth_header_admin)

    assert response.status_code == 400 or response.status_code == 422

    assert "error" in response.get_json() or "errors" in response.get_json()


