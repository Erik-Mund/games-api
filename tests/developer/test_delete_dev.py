import pytest
from models import Developer_profile

@pytest.mark.parametrize("header_fixture, developer_profile_fixture, expected_code", [
    ("auth_header_admin", "developer_profile", 204),
    ("auth_header_moderator", "developer_profile", 403),
    ("auth_header_developer", "developer_profile", 204),
    ("auth_header_developer", "other_developer_profile", 403),
    ("auth_header", "developer_profile", 403)
])
def test_delete_developer_permissions(client, request, developer_profile_fixture, expected_code, header_fixture):
    dev_profile = request.getfixturevalue(developer_profile_fixture)
    header = request.getfixturevalue(header_fixture)

    response = client.delete(f"/developers/{dev_profile.id}", headers=header)

    assert response.status_code == expected_code


def test_delete_developer_successful(client, session, auth_header_admin, developer_profile):
    response = client.delete(f"/developers/{developer_profile.id}", headers=auth_header_admin)

    assert response.status_code == 204

    deleted_developer = session.get(Developer_profile, developer_profile.id)
    assert deleted_developer is None

def test_delete_non_existing_developer(client, session, auth_header_admin):
    max_dev_id = session.query(Developer_profile.id).order_by(Developer_profile.id.desc()).first()
    invalid_dev_id = (max_dev_id[0] + 1) if max_dev_id else 1

    response = client.delete(f"/developers/{invalid_dev_id}", headers=auth_header_admin)

    assert response.status_code == 404

