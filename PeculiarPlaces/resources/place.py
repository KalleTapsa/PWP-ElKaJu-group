from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound, BadRequest
from models import (
    app, db, Place, 
    get_all_places, get_places_by_category, 
    get_places_by_application, get_places_by_user, create_place, delete_place
)


class PlaceConverter(BaseConverter):
    def to_python(self, value):
        db_place = Place.query.filter_by(id=value).first()
        if db_place is None:
            raise NotFound
        return db_place
        
    def to_url(self, value):
        return str(value.id)

app.url_map.converters['place'] = PlaceConverter

class PlaceCollection(Resource):
    def get(self):
        """Get all places with optional filtering"""
        trust_score = request.args.get("trust_score", 0, type=float)
        longitude = request.args.get("longitude", None, type=float)
        latitude = request.args.get("latitude", None, type=float)
        radius = request.args.get("radius", None, type=float)
        category = request.args.get("category", None, type=str)
        application = request.args.get("application", None, type=str)
        
        if category:
            places = get_places_by_category(category, trust_score=trust_score, longitude=longitude, latitude=latitude, radius=radius)
        elif application:
            places = get_places_by_application(application, trust_score=trust_score, longitude=longitude, latitude=latitude, radius=radius)
        else:
            places = get_all_places(trust_score=trust_score, longitude=longitude, latitude=latitude, radius=radius)
        
        res = [
            {
                "id": place.id,
                "name": place.name,
                "latitude": float(place.latitude),
                "longitude": float(place.longitude),
                "category": place.category,
                "trust_score": float(place.trust_score)
            } for place in places
        ]
        return res, 200

    def post(self):
        """Create a new place"""
        if request.content_type != 'application/json':
            return make_response(jsonify({"error": "Request content type must be JSON"}), 415)

        required_fields = ["name", "latitude", "longitude"]
        if not all(field in request.json for field in required_fields):
            raise BadRequest(description=f"Missing required fields: {required_fields}")

        try:
            place = create_place(
                user_id=request.json.get("user_id"),
                name=request.json["name"],
                latitude=float(request.json["latitude"]),
                longitude=float(request.json["longitude"]),
                description=request.json.get("description"),
                category=request.json.get("category"),
                address=request.json.get("address"),
                postal_code=request.json.get("postal_code"),
                city=request.json.get("city"),
                application=request.json.get("application")
            )
            location_url = f'/api/places/{place.id}/'
            return make_response(jsonify({"id": place.id, "message": "Place created successfully"}), 201, {'Location': location_url})
        except Exception as e:
            raise BadRequest(description=str(e))

class PlaceItem(Resource):
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
            "trust_score": float(place.trust_score)
        }, 200

    def put(self, place):
        """Update a place"""
        if request.content_type != 'application/json':
            return make_response(jsonify({"error": "Request content type must be JSON"}), 415)

        try:
            place.name = request.json.get("name", place.name)
            place.description = request.json.get("description", place.description)
            place.category = request.json.get("category", place.category)
            place.address = request.json.get("address", place.address)
            place.postal_code = request.json.get("postal_code", place.postal_code)
            place.city = request.json.get("city", place.city)
            if "latitude" in request.json:
                place.latitude = float(request.json["latitude"])
            if "longitude" in request.json:
                place.longitude = float(request.json["longitude"])
            place.application = request.json.get("application", place.application)
            
            db.session.commit()
            return {"message": "Place updated successfully"}, 200
        except Exception as e:
            raise BadRequest(description=str(e))

    def delete(self, place):
        """Delete a place"""
        delete_place(place.id)
        return make_response(jsonify({"message": "Place deleted successfully"}), 204)

class PlacesByUser(Resource):
    def get(self, user_id):
        """Get all places by a specific user"""
        places = get_places_by_user(user_id)
        res = [
            {
                "id": place.id,
                "name": place.name,
                "latitude": float(place.latitude),
                "longitude": float(place.longitude),
                "category": place.category,
                "trust_score": float(place.trust_score)
            } for place in places
        ]
        return res, 200
