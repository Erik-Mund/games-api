from permissions import UserRole, granted, denied


def can_delete_game(user, game):

    if user.role == UserRole.ADMIN:
        return granted()

    elif user.role == UserRole.MODERATOR:

        if game.report_count >= 10:
            return granted()
        else:
            return denied("game was not reported enough times")

    elif user.developer_profile:

        if not game.developer_profile:
            return denied("game has no developer")

        if game.developer_profile.user_id == user.id:
            return granted()
        else:
            return denied("the game belongs to another developer")

    else:
        return denied("invalid user role")

def can_upload_game(user):
    if user.role == UserRole.ADMIN:
        return granted()

    elif user.developer_profile:
        if user.deleted_games < 2:
            return granted()
        else:
            return denied("too much games were deleted")

    return denied("invalid user role")

def can_update_game(user, game):
    if user.role == UserRole.ADMIN:
        return granted()

    elif user.developer_profile:
        if not game.developer_profile:
            return denied("game has no developer")

        if game.developer_profile.user_id == user.id:
            return granted()
        else:
            return denied("the game belongs to another developer")

    return denied("invalid user role")
