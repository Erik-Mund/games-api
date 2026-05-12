import pytest
from GameBaseAPI.models import Review

@pytest.mark.parametrize("header_fixture, expected_code", [
    ("auth_header", 201),
    ("auth_header_other_user", 201),
    ("auth_header_moderator", 201),
    ("auth_header_admin", 201)
])
def test_report_review_permissions(client, request, review, expected_code, header_fixture, game):
    header = request.getfixturevalue(header_fixture)

    response = client.post(f"/games/{game.id}/reviews/{review.id}/report", headers=header)

    assert response.status_code == expected_code


def test_report_review_successful(client, session, auth_header_admin, game, review):
    response = client.post(f"/games/{game.id}/reviews/{review.id}/report", headers=auth_header_admin)

    assert response.status_code == 201

    reported_review = session.get(Review, review.id)
    assert reported_review.report_count == 1

def test_can_not_report_review_twice(client, session, auth_header_admin, game, review):
    response = client.post(f"/games/{game.id}/reviews/{review.id}/report", headers=auth_header_admin)

    assert response.status_code == 201

    reported_review = session.get(Review, review.id)
    assert reported_review.report_count == 1

    second_response = client.post(f"/games/{game.id}/reviews/{review.id}/report", headers=auth_header_admin)

    assert second_response.status_code == 403
    assert reported_review.report_count == 1