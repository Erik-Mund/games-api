import pytest
from models import Developer_profile

@pytest.mark.parametrize("header_fixture, user_fixture, expected_code", [
    ("auth_header", "user", 201),
    ("auth_header_developer", "developer", 403),
    ("auth_header_moderator", "moderator",  403), #as of now, while we have strict roles
    ("auth_header_admin", "admin", 201),
    ("auth_header", "other_user", 201)
])
def test_create_developer_profile_permissions(client, user_fixture, request, header_fixture, expected_code):
    header = request.getfixturevalue(header_fixture)
    user = request.getfixturevalue(user_fixture)

    data = {
        "studio_name":"Test studio"
    }

    response = client.post("/developers", json=data, headers=header)
    assert response.status_code == expected_code

def test_developer_profile_creation_successful(client, session, auth_header_admin, admin):
    data = {
        "studio_name":"Test studio"
    }

    response = client.post("/developers", json=data, headers=auth_header_admin)
    body = response.get_json()
    dev_id = body["id"]

    developer = session.get(Developer_profile, dev_id)
    assert developer is not None
    assert developer.user_id == admin.id
    assert developer.studio_name == "Test studio"

@pytest.mark.parametrize("studio_name, expected_status", [
    ("", 400),
    (None, 422),
    ("   ", 400)
])
def test_create_developer_invalid_input(client, studio_name, auth_header, expected_status):

    data = {
        "studio_name": studio_name
    }

    response = client.post("/developers", json=data, headers=auth_header)

    assert response.status_code == expected_status

    body = response.get_json()
    assert 'error' in body or 'errors' in body