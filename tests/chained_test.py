from models import Developer_profile, Game, Review
from conftest import client, session, user, auth_header, auth_header_admin, auth_header_other_user

def test_chain(client, session, user, other_user, auth_header, auth_header_admin, auth_header_other_user):
    dev_data = {
        #"user_id": user.id,
        "studio_name": "test developer"
    }
    dev_response = client.post("/developers", json=dev_data, headers=auth_header)

    assert dev_response.status_code == 201
    dev = dev_response.get_json()
    dev_id = dev["id"]

    #auth_header_dev = {"X-User-Id":user.id}

    game_data = {
        #"developer_profile_id": dev_id,
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
    review_response = client.post(f"/games/{game_id}/reviews", json=review_data, headers=auth_header_other_user)
    assert review_response.status_code == 201
    review = review_response.get_json()
    review_id = review["id"]

    dev_deletion_response = client.delete(f"/developers/{dev_id}", headers=auth_header_admin)
    assert dev_deletion_response.status_code == 204

    deleted_dev = session.get(Developer_profile, dev_id)
    deleted_game = session.get(Game, game_id)
    deleted_review = session.get(Review, review_id)

    assert deleted_game is None
    assert deleted_review is None
    assert deleted_dev is None

