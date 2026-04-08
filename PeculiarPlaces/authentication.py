from functools import wraps

from flask import g, jsonify, make_response, request
from werkzeug.exceptions import Forbidden

from PeculiarPlaces.models import User


def require_ownership(user_id):
    """
    Checks that the current user is the owner of the resource.
    """
    print(user_id, g.current_user.id)
    if not hasattr(g, "current_user"):
        raise Forbidden("Authentication required")

    if g.current_user.id != user_id:
        raise Forbidden("You do not own this resource")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        header = request.headers.get("Authorization")

        if not header:
            return make_response(
                jsonify({"error": "Missing Authorization header required"}), 401
            )

        header = header.lstrip("Bearer ")
        header = header.lstrip("bearer ")

        user = User.query.filter_by(api_key=header).first()

        if not user:
            return make_response(jsonify({"error": "Authentication required"}), 401)

        g.current_user = user

        return f(*args, **kwargs)

    return decorated_function
