import secrets

from flask import g
from flask_restful import Resource

from PeculiarPlaces import db
from PeculiarPlaces.authentication import login_required
from PeculiarPlaces.models import User

# Course example API used as a template for the file
class Users(Resource):
    """Resource for handling user registration and deletion."""

    def post(self):
        """
        Registers a new user and returns their API key.
        """
        api_key = secrets.token_hex(32)

        # No need to check for uniqueness since 2^256 possible keys

        user = User(api_key=api_key)
        db.session.add(user)
        db.session.commit()

        return {
            "id": user.id,
            "api_key": api_key,
            "message": "Save the API key. It will not be shown again.",
        }, 201

    @login_required
    def delete(self, user_id):
        """
        Deletes a user and all their associated data.
        """

        if g.current_user.id != user_id:
            return {"error": "You can only delete your own user"}, 403

        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        db.session.delete(user)
        db.session.commit()

        return {"message": "User and all associated data deleted successfully"}, 200
