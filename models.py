from database import db
from datetime import datetime

from permissions import UserRole
from passlib.hash import bcrypt

game_genre = db.Table(
    'game_genre',
    db.Column('game_id', db.Integer, db.ForeignKey('game.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
    #db.Column('developer_profile_id', db.Integer, db.ForeignKey('developer_profile.id'), primary_key=True)
)

class Developer_profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studio_name = db.Column(db.String(150), nullable=False, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True) # user_id is stored here to simplify checkings in the other scripts
    user = db.relationship("User", back_populates="developer_profile")

    games = db.relationship("Game", back_populates="developer_profile", cascade="all, delete")

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "studio_name": self.studio_name
        }


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    game_count = db.Column(db.Integer, default=0)

    games = db.relationship(
        "Game",
        secondary=game_genre,
        back_populates="genres"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Game(db.Model):
    __table_args__ = (db.UniqueConstraint("developer_profile_id", "title", name="unique_dev_title"),)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    release_year = db.Column(db.Integer)
    summary = db.Column(db.String(5000))
    platform = db.Column(db.String(300))
    price = db.Column(db.Integer)  # None or 0 = free

    review_count = db.Column(db.Integer, default=0, nullable=False)
    average_rating = db.Column(db.Float, default=0.0, nullable=False)

    report_count = db.Column(db.Integer, default=0)

    # Foreign key → Developer
    developer_profile_id = db.Column(db.Integer, db.ForeignKey("developer_profile.id"))

    # Relationship
    developer_profile = db.relationship("Developer_profile", back_populates="games")

    #user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    #user = db.relationship("User", back_populates="games")

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    genres = db.relationship(
        "Genre",
        secondary=game_genre,
        back_populates="games"
    )

    reviews = db.relationship(
        "Review",
        back_populates="game",
        cascade="all, delete"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "release_year": self.release_year,
            "summary": self.summary,
            "platform": self.platform,
            "price": self.price,
            "review_count": self.review_count,
            "average_rating": self.average_rating,
            "developer": self.developer_profile.to_dict() if self.developer_profile else None
        }
    def add_review_incremental(self, new_score):
        if self.review_count == 0:
            self.review_count = 1
            self.average_rating = float(new_score)
        else:
            total = self.average_rating * self.review_count
            self.review_count += 1
            self.average_rating = (total + new_score) / self.review_count

    def update_review_incremental(self, old_score, new_score):
        if self.review_count <= 0:
            raise ValueError("Cannot update rating when review_count is zero")

        total = self.average_rating * self.review_count
        self.average_rating = (total - old_score + new_score) / self.review_count

    def delete_review_incremental(self, old_score):
        if self.review_count <= 1:
            self.review_count = 0
            self.average_rating = 0.0
        else:
            total = self.average_rating * self.review_count
            self.review_count -= 1
            self.average_rating = (total - old_score) / self.review_count


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    #user_id = db.Column(db.Integer)
    report_count = db.Column(db.Integer, default=0)

    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(400))

    # FK → Game
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
    game = db.relationship("Game", back_populates="reviews")

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="reviews")

    __table_args__ = (db.UniqueConstraint("user_id", "game_id", name="unique_user_game_review"),)



    created_at = db.Column(
        db.DateTime, # type - date time
        default=datetime.utcnow, # default value when a row is created - current time by UTC
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow, # automatically updated when PUT is called
        nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "score": self.score,
            "comment": self.comment
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(300), unique=True, nullable=False)

    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.USER)
    name = db.Column(db.String(30), nullable=False, unique=True)

    password_hash = db.Column(db.String(128))

    deleted_reviews = db.Column(db.Integer, default=0)
    deleted_games = db.Column(db.Integer, default=0)

    reviews = db.relationship("Review", back_populates="user", cascade="all, delete")
    #games = db.relationship("Game", back_populates="user")

    #developer_profile_id = db.Column(db.Integer, db.ForeignKey("developer_profile.id"), nullable=False)
    developer_profile = db.relationship("Developer_profile", back_populates="user", uselist=False, cascade="all, delete-orphan") #uselist - flags that only one object can be stored

    def set_password(self, password: str):
        if not isinstance(password, str):
            raise ValueError("Password must be a string")
        self.password_hash = bcrypt.hash(password)

    def check_password(self, password):
        return bcrypt.verify(password, self.password_hash)

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "name": self.name,
            "deleted_reviews": self.deleted_reviews,
            "deleted_games": self.deleted_games,
            "reviews": [r.to_dict() for r in self.reviews],
            "developer_profile": self.developer_profile.to_dict() if self.developer_profile else None
        }


class TokenBlockList(db.Model):
    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime)






