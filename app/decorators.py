from flask import request, abort


def has_header_secret(secret=None, header="X-API-SECRET"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if secret and request.headers.get(header) != secret:
                abort(404)
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator
