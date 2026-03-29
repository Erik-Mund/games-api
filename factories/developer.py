from models import Developer_profile
from database import db


def make_developer_profile(user, studio_name):
    existing = Developer_profile.query.filter_by(user_id=user.id).first()
    if existing:
        return existing

    existing_name = Developer_profile.query.filter_by(studio_name=studio_name).first()
    if existing_name:
        raise ValueError("Studio name already taken")

    profile = Developer_profile(
        user_id=user.id,
        studio_name=studio_name
    )

    db.session.add(profile)
    db.session.commit()

    return profile


def update_developer_profile(profile, studio_name):
    if profile.studio_name != studio_name:
        profile.studio_name = studio_name
        db.session.commit()

    return profile


def delete_developer_profile(profile):
    db.session.delete(profile)
    db.session.commit()

    return True
