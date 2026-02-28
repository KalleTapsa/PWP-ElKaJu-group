from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound, BadRequest
from models import (
    app, db, Image, 
    get_images_by_place, 
    get_images_by_user, create_image, delete_image
)

class ImageConverter(BaseConverter):
    def to_python(self, value):
        db_image = Image.query.filter_by(id=value).first()
        if db_image is None:
            raise NotFound
        return db_image
        
    def to_url(self, value):
        return str(value.id)

app.url_map.converters['image'] = ImageConverter

class ImageCollection(Resource):
#    def get(self):
  #      """Get all images with optional filtering"""
   #     trust_score = request.args.get("trust_score", 0, type=float)
    #    imagepath = request.args.get("imagepath", None, type=str)
     #   description = request.args.get("description", None, type=str)
      #  timestamp = request.args.get("timestamp", None, type=datetime)
       # application = request.args.get("application", None, type=str)

    def post(self):
        """Create a new image"""
        if request.content_type != 'application/json':
            return make_response(jsonify({"error": "Request content type must be JSON"}), 415)

        required_fields = ["imagepath", "timestamp"]
        if not all(field in request.json for field in required_fields):
            raise BadRequest(description=f"Missing required fields: {required_fields}")

        try:
            image = create_image(
                user_id=request.json.get("user_id"),
                place_id=request.json.get("place_id"),
                imagepath=request.json["imagepath"],
                timestamp=request.json["timestamp"],
                description=request.json.get("description"),
                application=request.json.get("application")
            )
            location_url = f'/api/images/{image.id}/'
            return make_response(jsonify({"id": image.id, "message": "Image created successfully"}), 201)
        except Exception as e:
            raise BadRequest(description=str(e))

class ImageItem(Resource):
    def get(self, image):
        """Get a specific image by ID"""
        return {
            "id": image.id,
            "user_id": image.user_id,
            "place_id": image.place_id,
            "imagepath": image.imagepath,
            "description": image.description,
            "timestamp": image.timestamp,
            "application": image.application,
            "trust_score": float(image.trust_score)
        }, 200

    def put(self, image):
        """Update an image"""
        if request.content_type != 'application/json':
            return make_response(jsonify({"error": "Request content type must be JSON"}), 415)

        try:
            image.imagepath = request.json.get("imagepath", image.imagepath)
            image.description = request.json.get("description", image.description)
            image.timestamp = request.json.get("timestamp", image.timestamp)
            image.application = request.json.get("application", image.application)
            image.trust_score = request.json.get("trust_score", image.trust_score)
            
            db.session.commit()
            return {"message": "Image updated successfully"}, 200
        except Exception as e:
            raise BadRequest(description=str(e))

    def delete(self, image):
        """Delete an image"""
        delete_image(image.id)
        return make_response(jsonify({"message": "Image deleted successfully"}), 204)

class ImagesByUser(Resource):
    def get(self, user_id):
        """Get all images by a specific user"""
        images = get_images_by_user(user_id)
        res = [
            {
                "id": image.id,
                "imagepath": image.imagepath,
                "description": image.description,
                "timestamp": image.timestamp,
                "application": image.application,
                "trust_score": float(image.trust_score)
            } for image in images
        ]
        return res, 200
    
class ImagesByPlace(Resource):
    def get(self, place_id):
        """Get all images for a specific place"""
        images = get_images_by_place(place_id)
        res = [
            {
                "id": image.id,
                "imagepath": image.imagepath,
                "description": image.description,
                "timestamp": image.timestamp,
                "application": image.application,
                "trust_score": float(image.trust_score)
            } for image in images
        ]
        return res, 200
