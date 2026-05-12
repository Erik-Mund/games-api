from enum import Enum

def granted():
    return True, "permission granted"

def denied(reason):
    return False, reason


class UserRole(str, Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


