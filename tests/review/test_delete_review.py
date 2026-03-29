import pytest
from models import Review

@pytest.mark.parametrize("header_fixture, review_fixture, expected_code", [
    ("auth_header", "review", 204),
    ("auth_header_other_user", "review", 403),
    ("auth_header_moderator", "review", 403),
    ("auth_header_moderator", "reported_review", 204),
    ("auth_header_admin", "review", 204)
])
def test_delete_review_permissions(client, request, review_fixture, expected_code, header_fixture, game):
    review = request.getfixturevalue(review_fixture)
    header = request.getfixturevalue(header_fixture)

    response = client.delete(f"/games/{game.id}/reviews/{review.id}", headers=header)

    assert response.status_code == expected_code


def test_delete_review_successful(client, session, auth_header_admin, game, review):
    response = client.delete(f"/games/{game.id}/reviews/{review.id}", headers=auth_header_admin)

    assert response.status_code == 204

    deleted_review = session.get(Review, review.id)
    assert deleted_review is None