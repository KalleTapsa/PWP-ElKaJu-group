from flask import g, jsonify, make_response, request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest, NotFound

from PeculiarPlaces import db
from PeculiarPlaces.authentication import login_required, require_ownership
from PeculiarPlaces.utils import (
    create_place,
    delete_place,
    get_all_places,
    get_places_by_application,
    get_places_by_category,
    get_places_by_user,
    get_user_by_id,
)


class Places(Resource):
    """Resource for handling places."""
    method_decorators = {"get": [], "post": [login_required]}

    def get(self):
        """Get all places with optional filtering"""
        trust_score = request.args.get("trust_score", 0, type=float)
        longitude = request.args.get("longitude", None, type=float)
        latitude = request.args.get("latitude", None, type=float)
        radius = request.args.get("radius", None, type=float)
        category = request.args.get("category", None, type=str)
        application = request.args.get("application", None, type=str)

        if category:
            places = get_places_by_category(
                category,
                trust_score=trust_score,
                longitude=longitude,
                latitude=latitude,
                radius=radius,
            )
        elif application:
            places = get_places_by_application(
                application,
                trust_score=trust_score,
                longitude=longitude,
                latitude=latitude,
                radius=radius,
            )
        else:
            places = get_all_places(
                trust_score=trust_score,
                longitude=longitude,
                latitude=latitude,
                radius=radius,
            )

        res = [
            {
                "id": place.id,
                "name": place.name,
                "latitude": float(place.latitude),
                "longitude": float(place.longitude),
                "category": place.category,
                "trust_score": float(place.trust_score),
            }
            for place in places
        ]
        return res, 200

    def post(self):
        """Create a new place"""
        if request.content_type != "application/json":
            return make_response(
                jsonify({"error": "Request content type must be JSON"}), 415
            )

        required_fields = ["name", "latitude", "longitude"]
        missing = [f for f in required_fields if f not in request.json]
        if missing:
            raise BadRequest(description=f"Missing required fields: {missing}")

        if request.json["name"] is None or str(request.json["name"]).strip() == "":
            raise BadRequest(description="name cannot be null or empty")

        for field in ["latitude", "longitude"]:
            value = request.json[field]
            if value is None or (isinstance(value, str) and value.strip() == ""):
                raise BadRequest(description=f"{field} cannot be null or empty")
            try:
                float(value)
            except (TypeError, ValueError) as exc:
                raise BadRequest(description=f"{field} must be a valid number") from exc

        try:
            place = create_place(
                user_id=g.current_user.id,
                name=request.json["name"],
                latitude=float(request.json["latitude"]),
                longitude=float(request.json["longitude"]),
                description=request.json.get("description"),
                category=request.json.get("category"),
                address=request.json.get("address"),
                postal_code=request.json.get("postal_code"),
                city=request.json.get("city"),
                application=request.json.get("application"),
            )
            location_url = f"/api/places/{place.id}/"
            return make_response(
                jsonify({"id": place.id, "message": "Place created successfully"}),
                201,
                {"Location": location_url},
            )
        except Exception as e:
            raise BadRequest(description=str(e)) from e


class PlaceItem(Resource):
    method_decorators = {
        "get": [],
        "put": [login_required],
        "delete": [login_required],
    }

    def get(self, place):
        """Get a specific place by ID"""
        return {
            "id": place.id,
            "user_id": place.user_id,
            "name": place.name,
            "description": place.description,
            "category": place.category,
            "address": place.address,
            "postal_code": place.postal_code,
            "city": place.city,
            "latitude": float(place.latitude),
            "longitude": float(place.longitude),
            "application": place.application,
            "trust_score": float(place.trust_score),
        }, 200

    def put(self, place):
        """Update a place"""

        require_ownership(place.user_id)

        if request.content_type != "application/json":
            return make_response(
                jsonify({"error": "Request content type must be JSON"}), 415
            )

        data = request.get_json(silent=True) or {}

        if "name" in data and not str(data["name"] or "").strip():
            raise BadRequest(description="name cannot be null or empty")

        for field in ("latitude", "longitude"):
            if field in data:
                value = data[field]
                if value is None or (isinstance(value, str) and not value.strip()):
                    raise BadRequest(description=f"{field} cannot be null or empty")
                try:
                    setattr(place, field, float(value))
                except (TypeError, ValueError) as exc:
                    raise BadRequest(
                        description=f"{field} must be a valid number"
                    ) from exc

        for field in (
            "name",
            "description",
            "category",
            "address",
            "postal_code",
            "city",
            "application",
        ):
            if field in data:
                setattr(place, field, data[field])

        try:
            db.session.commit()
        except Exception as e:
            raise BadRequest(description=str(e)) from e

        return {"message": "Place updated successfully"}, 200

    def delete(self, place):
        """Delete a place"""

        require_ownership(place.user_id)

        delete_place(place.id)
        return {"message": "Place deleted successfully"}, 200


class PlacesByUser(Resource):
    def get(self, user_id):
        """Get all places by a specific user"""
        if not get_user_by_id(user_id):
            raise NotFound(description="User not found")
        places = get_places_by_user(user_id)
        res = [
            {
                "id": place.id,
                "name": place.name,
                "latitude": float(place.latitude),
                "longitude": float(place.longitude),
                "category": place.category,
                "trust_score": float(place.trust_score),
            }
            for place in places
        ]
        return res, 200
