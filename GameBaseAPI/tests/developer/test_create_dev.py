import pytest
from GameBaseAPI.models import Developer_profile

@pytest.mark.parametrize("header_fixture, expected_code", [
    ("auth_header", 201),
    ("auth_header_developer", 403),
    ("auth_header_moderator", 201),
    ("auth_header_admin", 201)
])
def test_create_developer_profile_permissions(client, developer_profile, request, header_fixture, expected_code):
    header = request.getfixturevalue(header_fixture)

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

def test_one_developer_profile_per_user(client, session, auth_header_admin, admin):
    data = {
        "studio_name": "Test studio"
    }

    response = client.post("/developers", json=data, headers=auth_header_admin)
    body = response.get_json()
    dev_id = body["id"]

    developer = session.get(Developer_profile, dev_id)
    assert developer is not None

    second_response = client.post("/developers", json=data, headers=auth_header_admin)
    assert second_response.status_code == 403
    body = second_response.get_json()
    assert "error" in body or "errors" in body

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