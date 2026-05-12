from GameBaseAPI.utilities.permissions import UserRole, granted, denied

def can_delete_review(user, review):
    if user.role == UserRole.ADMIN:
        return granted()

    elif user.role == UserRole.MODERATOR:
        if user.id == review.user_id:
            return granted()
        elif review.report_count >= 3:
            return granted()
        return denied("the review wasn't reported enough times")

    else:
        if not review.user_id:
            return denied("author not found")
        elif user.id == review.user_id:
            return granted()

        return denied("the review belongs to another user")

def can_upload_review(user):
    if user.role == UserRole.ADMIN:
        return granted()

    else:
        if user.deleted_reviews < 5:
            return granted()
        else:
            return denied("too many reports received")

def can_update_review(user, review):
    if review.user_id is None:
        return denied("author not found")
    elif user.id == review.user_id:
        return granted()

    return denied("the review belongs to another user")

def can_report_review(user, review):
    if review in user.reported_reviews:
        return denied("Review already reported")
    else:
        return granted()
