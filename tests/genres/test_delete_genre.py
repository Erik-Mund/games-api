import pytest
from models import Genre

@pytest.mark.parametrize("header_fixture, genre_fixture, expected_code", [
    ("auth_header_admin", "genre", 204),
    ("auth_header_moderator", "big_genre", 403),
    ("auth_header_moderator", "genre", 204),
    ("auth_header_developer", "genre", 403),
    ("auth_header", "genre", 403)
])
def test_delete_genre_permissions(client, request, genre_fixture, expected_code, header_fixture):
    genre = request.getfixturevalue(genre_fixture)
    header = request.getfixturevalue(header_fixture)

    response = client.delete(f"/genres/{genre.id}", headers=header)

    assert response.status_code == expected_code


def test_delete_genre_successful(client, session, auth_header_admin, genre):
    response = client.delete(f"/genres/{genre.id}", headers=auth_header_admin)

    assert response.status_code == 204

    deleted_genre = session.get(Genre, genre.id)
    assert deleted_genre is None

def test_delete_non_existing_genre(client, session, auth_header_admin):
    max_genre_id = session.query(Genre.id).order_by(Genre.id.desc()).first()
    invalid_id = max_genre_id[0] + 1 if max_genre_id else 1

    response = client.delete(f"/genres/{invalid_id}", headers=auth_header_admin)

    assert response.status_code == 404