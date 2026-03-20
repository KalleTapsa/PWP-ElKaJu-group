import secrets
from flask import g
from flask_restful import Resource
from ..models import User
from .. import db
from ..authentication import require_api_key, require_ownership
from werkzeug.security import generate_password_hash


class Users(Resource):
    def post(self):
        """
        Registers a new user and returns their API key.
        """
        api_key = secrets.token_hex(32)

        #No need to check for uniqueness since the sun will explode before we get a collision with 2^256 possible keys

        hashed_key = generate_password_hash(api_key)
        user = User(api_key=hashed_key)
        db.session.add(user)
        db.session.commit()

        return {
            "id": user.id,
            "api_key": api_key,
            "message": "Save the API key. It will not be shown again."
        }, 201
    
    @require_api_key
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