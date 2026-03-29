from permissions import UserRole, granted, denied

def can_delete_genres(user, genre):
    if user.role == UserRole.ADMIN:
        if genre.game_count is None:
            return True, "invalid genre data"
        return granted()

    elif user.role == UserRole.MODERATOR:
        if genre.game_count is None:
            return denied("invalid genre data")

        if genre.game_count < 50:
            return granted()
        else:
            return denied("the genre has too many games")

    return denied("your role not allowed to perform the action")

def can_upload_genres(user):
    if user.role in (UserRole.ADMIN, UserRole.MODERATOR):
        return granted()

    return denied("role not allowed to perform the action")