from flask import g, abort, current_app

def authorize(check_func, *args):
    user = g.current_user
    allowed, reason = check_func(user, *args)

    if not allowed:
        current_app.logger.warning("authorization failed")
        abort(403, description=reason)

    return True