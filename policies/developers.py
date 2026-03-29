from permissions import UserRole, granted, denied

def can_delete_developer(user, developer_profile):
    if user.role == UserRole.ADMIN:
        return granted()
    elif user.developer_profile is not None:
        if user.developer_profile == developer_profile:
            return granted()
        else:
            return denied("developer profile belongs to another user")
    return denied("invalid user role")

def can_create_developer(user):
    if user.role == UserRole.ADMIN:
        return granted()
    elif user.role == UserRole.USER:
        if user.developer_profile is None:
            return granted()
        else:
            return denied("user already has a developer profile")
    elif user.role == UserRole.DEVELOPER:
        return denied("user already has a developer profile")

    return denied("role not allowed to create a developer profile")

def can_update_developer(user, developer_profile):
    if user.role == UserRole.ADMIN:
        return granted()
    elif user.developer_profile is not None:
        if not user.developer_profile:
            denied("user's developer profile not found")

        if user.id == developer_profile.user_id:
            return granted()
        else:
            return denied("the developer profile belongs to another user")

    return denied("user is not a developer")
