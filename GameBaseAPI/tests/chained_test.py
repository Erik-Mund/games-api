from GameBaseAPI.models import Developer_profile, Game, Review
from GameBaseAPI.tests.conftest import login_as

def test_chain(client, session, user, admin, other_user):
    dev_data = {
        "studio_name": "test developer"
    }
    auth_header = login_as(client, user)
    dev_response = client.post("/developers", json=dev_data, headers=auth_header)
    print(dev_response.get_json())

    assert dev_response.status_code == 201
    dev = dev_response.get_json()
    dev_id = dev["id"]

    game_data = {
        "title": "test game",
        "price": 5
    }
    game_response = client.post("/games", json=game_data, headers=auth_header) # I guess should work here cuz user now has dev profile
    assert game_response.status_code == 201
    game = game_response.get_json()
    game_id = game["id"]

    update_game_data = {
        "price": 10
    }

    updated_game_response = client.put(f"/games/{game_id}", json=update_game_data, headers=auth_header) # will it only update the price field?
    assert updated_game_response.status_code == 200
    updated_game = session.get(Game, game_id)

    assert updated_game.price == 10
    assert updated_game.title == "test game"

    review_data = {
        "score": 5
    }

    auth_header_other_user = login_as(client, other_user)
    review_response = client.post(f"/games/{game_id}/reviews", json=review_data, headers=auth_header_other_user)
    assert review_response.status_code == 201
    review = review_response.get_json()
    review_id = review["id"]

    auth_header_admin = login_as(client, admin)
    dev_deletion_response = client.delete(f"/developers/{dev_id}", headers=auth_header_admin)
    assert dev_deletion_response.status_code == 204

    deleted_dev = session.get(Developer_profile, dev_id)
    deleted_game = session.get(Game, game_id)
    deleted_review = session.get(Review, review_id)

    assert deleted_game is None
    assert deleted_review is None
    assert deleted_dev is None

