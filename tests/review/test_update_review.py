from models import Review
import pytest

@pytest.mark.parametrize("header_fixture, expected_code", [
    ("auth_header_admin", 200),
    ("auth_header_moderator", 403), # both mods
    ("auth_header_developer", 403),  # and devs can edit own reviews but the review fixture is tied to a user so should be invalid
    ("auth_header", 200),
    ("auth_header_other_user", 403)
])
def test_update_review_permissions(client, session, request, header_fixture, expected_code, review, game):
    header = request.getfixturevalue(header_fixture)

    data = {
        "score": 1,
        "comment": "changed my mind"
    }

    response = client.put(f"/games/{game.id}/reviews/{review.id}", json=data, headers=header)

    assert response.status_code == expected_code
    if expected_code == 403:
        assert session.get(Review, review.id).score != 1

def test_update_review_successful(client, session, review, game, auth_header_admin):
    data = {
        "score": 4,
        "comment": "better now"
    }

    client.put(f"/games/{game.id}/reviews/{review.id}", json=data, headers=auth_header_admin)

    updated = session.get(Review, review.id)

    assert updated.score == 4
    assert updated.comment == "better now"

def test_review_invalid_score_rejected(client, review, game, auth_header_admin):
    data = {
        "score": -1
    }

    response = client.put(f"/games/{game.id}/reviews/{review.id}", json=data, headers=auth_header_admin)

    assert response.status_code == 422

    body = response.get_json()
    assert "errors" in body

def test_update_non_existing_review(client, session, game, auth_header_admin):
    max_review_id = session.query(Review.id).order_by(Review.id.desc()).first()
    invalid_review_id = (max_review_id[0] + 1) if max_review_id else 1

    data = {
        "score": 3
    }

    response = client.put(f"/games/{game.id}/reviews/{invalid_review_id}", json=data, headers=auth_header_admin)

    assert response.status_code == 404

