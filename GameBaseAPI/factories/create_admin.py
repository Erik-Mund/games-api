from GameBaseAPI.app import create_app
from GameBaseAPI.database import db
from GameBaseAPI.models import User, UserRole

app = create_app()

with app.app_context():

    user = User(
        name="admin",
        email="admin@example.com",
        role=UserRole.ADMIN
    )
    user.set_password("Admin123")

    print(user)
    print(user.check_password("Admin123"))

    db.session.add(user)
    db.session.commit()