def get_csrf(client, is_access=True):
    name = "csrf_access_token"
    if not is_access:
        name = "csrf_refresh_token"
    csrf_token = client.get_cookie(name)
    if csrf_token is None:
        raise RuntimeError(f"Missing CSRF token: {name}")
    return csrf_token.value

