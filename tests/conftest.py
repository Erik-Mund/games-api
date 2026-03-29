import pytest

from app import create_app
from database import db
from models import User, UserRole, Developer_profile, Game, Review, Genre

from sqlalchemy.orm import sessionmaker


# --------------------
# App
# --------------------

@pytest.fixture
def app():
    app = create_app("testing")  # or however you init app

    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # changes the database we're operating with atm; memory - temporary, per-session one
        "WTF_CSRF_ENABLED": False # disables CSRF token security
    })

    with app.app_context():
        db.create_all()
        yield app #returns, pauses the function
        db.drop_all() #deletes all tables from the DB


# --------------------
# Client
# --------------------

@pytest.fixture
def client(app):
    return app.test_client() # creates a fake browser


# --------------------
# Database
# --------------------

@pytest.fixture
def session(app): # centralizes the session logic
    with app.app_context():
        yield db.session
        db.session.rollback()


# --------------------
# Users
# --------------------

@pytest.fixture
def user(session): # fakes users, takes a custom session as a variable for it to be more universal in the future
    user = User(
        name="user1",
        role=UserRole.USER,
        email="user_test@example.com"
    )
    user.set_password("Password123")

    session.add(user)
    session.commit()

    return user

@pytest.fixture
def other_user(session):
    other_user = User(
        name="user2",
        role=UserRole.USER,
        email="other_user_test@example.com"
    )
    other_user.set_password("Password123")

    session.add(other_user)
    session.commit()

    return other_user

@pytest.fixture
def reported_user(session): # fakes users, takes a custom session as a variable for it to be more universal in the future
    user = User(
        name="user3",
        role=UserRole.USER,
        deleted_reviews=10,
        email="reported_user_test@example.com"
    )
    user.set_password("Password123")

    session.add(user)
    session.commit()

    return user


@pytest.fixture
def developer(session):
    dev = User(
        name="dev1",
        role=UserRole.DEVELOPER,
        email="dev_test@example.com"
    )
    dev.set_password("Password123")

    session.add(dev)
    session.commit()

    return dev

@pytest.fixture
def other_developer(session):
    dev = User(
        name="dev2",
        role=UserRole.DEVELOPER,
        email="other_dev_test@example.com"
    )
    dev.set_password("Password123")

    session.add(dev)
    session.commit()

    return dev

@pytest.fixture
def reported_developer(session):
    dev = User(
        name="dev3",
        role=UserRole.DEVELOPER,
        deleted_games=5,
        email="reported_dev_test@example.com"
    )
    dev.set_password("Password123")

    session.add(dev)
    session.commit()

    return dev


@pytest.fixture
def moderator(session):
    mod = User(name="mod1", role=UserRole.MODERATOR, email="moderator_test@example.com")
    mod.set_password("Password123")

    session.add(mod)
    session.commit()

    return mod


@pytest.fixture
def admin(session):
    admin = User(
        name="admin1",
        role=UserRole.ADMIN,
        email="admin_test@example.com"
    )
    admin.set_password("Password123")

    session.add(admin)
    session.commit()

    return admin

@pytest.fixture
def developer_profile(session, developer):
    developer_profile = Developer_profile(user_id=developer.id, studio_name="Test Profile")

    session.add(developer_profile)
    session.commit()

    return developer_profile

@pytest.fixture
def other_developer_profile(session, other_developer):
    developer_profile = Developer_profile(user_id=other_developer.id, studio_name="Test Profile 2")

    session.add(developer_profile)
    session.commit()

    return developer_profile

@pytest.fixture
def admin_developer_profile(session, admin):
    developer_profile = Developer_profile(user_id=admin.id, studio_name="Admin Profile")

    session.add(developer_profile)
    session.commit()

    return developer_profile

@pytest.fixture
def reported_developer_profile(session, reported_developer):
    developer_profile = Developer_profile(user_id=reported_developer.id, studio_name="Test Profile 3")

    session.add(developer_profile)
    session.commit()

    return developer_profile

@pytest.fixture
def game(session, developer_profile):
    game = Game(developer_profile_id=developer_profile.id, title="Test Game", price=5)

    session.add(game)
    session.commit()

    return game

@pytest.fixture
def other_game(session, other_developer_profile):
    game = Game(developer_profile_id=other_developer_profile.id, title="Test Game 2", price=5)

    session.add(game)
    session.commit()

    return game

@pytest.fixture
def reported_game(session, developer_profile):
    game = Game(developer_profile_id=developer_profile.id, title="Test Game", price=5, report_count=100)

    session.add(game)
    session.commit()

    return game

@pytest.fixture
def review(session, user, game):
    review = Review(game_id=game.id, user=user, score=5, comment="Test comment")

    session.add(review)

    game.review_count += 1
    game.average_rating = 5

    session.commit()

    return review

@pytest.fixture
def genre(session):
    genre = Genre(name="Test Genre")

    session.add(genre)
    session.commit()

    return genre

@pytest.fixture
def big_genre(session):
    genre = Genre(name="Test Genre", game_count=100)

    session.add(genre)
    session.commit()

    return genre

@pytest.fixture
def reported_review(session, user, game):
    review = Review(game_id=game.id, user=user, score=4, comment="Test reported comment", report_count=11)

    session.add(review)
    session.commit()

    return review


@pytest.fixture
def game_data(developer_profile):
    def factory(**overrides):
        data = {
            "title": "Test Game",
            "price": 10,
            #"developer_profile_id": developer_profile.id,
            "summary": "this is a good game"
        }
        data.update(overrides)

        return data

    return factory

# --------------------
# Auth Headers (Mock)
# --------------------

@pytest.fixture
def auth_header(client, user):    # centralizes generation of auth_header necessary to fake logins for tests
    response = client.post("/login", json={
        "email": user.email,
        "password": "Password123"
    })
    token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def auth_header_other_user(client, other_user):    # centralizes generation of auth_header necessary to fake logins for tests
    response = client.post("/login", json={
        "email": other_user.email,
        "password": "Password123"
    })
    token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def auth_header_reported_user(client, reported_user):    # centralizes generation of auth_header necessary to fake logins for tests
    response = client.post("/login", json={
        "email": reported_user.email,
        "password": "Password123"
    })
    token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def auth_header_developer(client, developer):    # centralizes generation of auth_header necessary to fake logins for tests
    response = client.post("/login", json={
        "email": developer.email,
        "password": "Password123"
    })
    token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def auth_header_other_developer(client, other_developer):    # centralizes generation of auth_header necessary to fake logins for tests
    response = client.post("/login", json={
        "email": other_developer.email,
        "password": "Password123"
    })
    token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def auth_header_reported_developer(client, reported_developer):   # centralizes generation of auth_header necessary to fake logins for tests
    response = client.post("/login", json={
        "email": reported_developer.email,
        "password": "Password123"
    })
    token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def auth_header_moderator(client, moderator):    # centralizes generation of auth_header necessary to fake logins for tests
    response = client.post("/login", json={
        "email": moderator.email,
        "password": "Password123"
    })
    token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def auth_header_admin(client, admin):    # centralizes generation of auth_header necessary to fake logins for tests
    response = client.post("/login", json={
        "email": admin.email,
        "password": "Password123"
    })
    token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }