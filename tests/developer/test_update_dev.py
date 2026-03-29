import pytest
from models import Developer_profile

@pytest.mark.parametrize("header_fixture, developer_profile_fixture, expected_code", [
    ("auth_header", "developer_profile", 403),
    ("auth_header_developer", "developer_profile", 200),
    ("auth_header_developer", "other_developer_profile", 403),
    ("auth_header_moderator", "developer_profile", 403), #as of now, while we have strict roles
    ("auth_header_admin", "developer_profile", 200)
])
def test_update_developer_profile_permissions(client,session, request, header_fixture, expected_code, developer_profile_fixture):
    header = request.getfixturevalue(header_fixture)
    dev_profile = request.getfixturevalue(developer_profile_fixture)

    data = {
        "studio_name":"Test studio updated"
    }

    response = client.put(f"/developers/{dev_profile.id}", json=data, headers=header)
    assert response.status_code == expected_code

    if expected_code == 403:
        assert session.get(Developer_profile, dev_profile.id).studio_name != "Test studio updated"

def test_developer_profile_update_successful(client, developer_profile, session, auth_header_admin):
    data = {
        "studio_name":"Test studio updated"
    }

    response = client.put(f"/developers/{developer_profile.id}", json=data, headers=auth_header_admin)
    assert response.status_code == 200

    developer = session.get(Developer_profile, developer_profile.id)
    assert developer is not None
    assert developer.user_id == developer_profile.user_id #since it wasn't changed
    assert developer.studio_name == "Test studio updated"

@pytest.mark.parametrize("studio_name, expected_status", [
    ("", 400),
    (None, 422)
])
def test_update_developer_invalid_input(client, developer_profile, studio_name, auth_header_admin, expected_status):

    data = {
        "studio_name": studio_name
    }

    response = client.put(f"/developers/{developer_profile.id}", json=data, headers=auth_header_admin)

    assert response.status_code == expected_status

    body = response.get_json()
    assert 'error' in body or 'errors' in body

def test_update_non_existing_developer(client, session, auth_header_admin):
    max_dev_id = session.query(Developer_profile.id).order_by(Developer_profile.id.desc()).first() #returns a tuple or none
    invalid_dev_id = (max_dev_id[0] + 1) if max_dev_id else 1

    data = {
        "studio_name": "updated name"
    }

    response = client.put(f"/developers/{invalid_dev_id}", json=data, headers=auth_header_admin)

    assert response.status_code == 404