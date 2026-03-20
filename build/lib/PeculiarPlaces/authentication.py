from functools import wraps
from flask import g
from flask_api_key import api_key_required
from werkzeug.exceptions import Forbidden

def require_api_key(func):
    """
    Checks the API key is valid and then sets current_user.
    """
    @api_key_required
    @wraps(func)
    def wrapper(*args, **kwargs):
        from .models import User
        user = User.query.filter_by(api_key=g.api_key).first()
        if user is None:
            raise Forbidden("Invalid API key")
        g.current_user = user
        return func(*args, **kwargs)
    return wrapper

def require_ownership(user_id):
    """
    Checks that the current user is the owner of the resource.
    """
    if g.current_user.id != user_id:
        raise Forbidden("You do not own this resource")