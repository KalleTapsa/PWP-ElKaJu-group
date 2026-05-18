from flask import g, jsonify, make_response, request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest, NotFound

from ..authentication import login_required, require_ownership
from ..utils import (
    create_review,
    delete_review,
    get_place_by_id,
    get_review_by_id,
    get_reviews_by_place,
    get_reviews_by_user,
    get_user_by_id,
)

# Course example API used as a template for the file

class ReviewById(Resource):
    """Resource for handling individual reviews by their ID"""

    method_decorators = {"get": [], "delete": [login_required]}

    def get(self, place_id, review_id):
        """Get a specific review by its ID"""
        review = get_review_by_id(review_id)
        if not review or review.place_id != place_id:
            raise NotFound(description="Review not found")
        return {
            "id": review.id,
            "user_id": review.user_id,
            "place_id": review.place_id,
            "rating": review.rating,
            "text": review.text,
            "timestamp": review.timestamp.isoformat(),
            "trust_score": float(review.trust_score),
        }, 200

    def delete(self, place_id, review_id):
        """Delete a review"""
        review = get_review_by_id(review_id)
        if not review or review.place_id != place_id:
            raise NotFound(description="Review not found")

        require_ownership(review.user_id)

        delete_review(review_id)
        return make_response(jsonify({"message": "Review deleted successfully"}), 200)


class PlaceReviews(Resource):
    """Resource for handling reviews related to a specific place, get all reviews for a place and create new reviews"""

    method_decorators = {"get": [], "post": [login_required]}

    def get(self, place_id):
        """Get all reviews for a specific place"""
        if not get_place_by_id(place_id):
            raise NotFound(description="Place not found")
        reviews = get_reviews_by_place(place_id)
        res = [
            {
                "id": review.id,
                "user_id": review.user_id,
                "place_id": review.place_id,
                "rating": review.rating,
                "text": review.text,
                "timestamp": review.timestamp.isoformat(),
                "trust_score": float(review.trust_score),
            }
            for review in reviews
        ]
        return res, 200

    def post(self, place_id):
        """Create a new review for a specific place"""

        if request.content_type != "application/json":
            return make_response(
                jsonify({"error": "Request content type must be JSON"}), 415
            )

        required_fields = ["rating"]

        if not request.json or not all(
            field in request.json for field in required_fields
        ):
            raise BadRequest(description=f"Missing required fields: {required_fields}")

        if not get_place_by_id(place_id):
            raise NotFound(description="Place not found")

        try:
            rating = int(request.json["rating"])

            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")

            review = create_review(
                user_id=g.current_user.id,
                place_id=place_id,
                rating=rating,
                text=request.json.get("text"),
            )

            return make_response(
                jsonify({"id": review.id, "message": "Review created successfully"}),
                201,
            )

        except ValueError as e:
            raise BadRequest(description=str(e))
        except Exception as e:
            raise BadRequest(description=str(e))


class ReviewsByUser(Resource):
    """Resource for fetching all reviews made by a specific user."""

    def get(self, user_id):
        """Get all reviews by a specific user"""
        if not get_user_by_id(user_id):
            raise NotFound(description="User not found")
        reviews = get_reviews_by_user(user_id)
        res = [
            {
                "id": review.id,
                "user_id": review.user_id,
                "place_id": review.place_id,
                "rating": review.rating,
                "text": review.text,
                "timestamp": review.timestamp.isoformat(),
                "trust_score": float(review.trust_score),
            }
            for review in reviews
        ]
        return res, 200
