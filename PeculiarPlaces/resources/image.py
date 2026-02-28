from datetime import datetime
from flask import Flask, request, jsonify, make_response, current_app
from flask_restful import Api, Resource
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound, BadRequest
from werkzeug.utils import secure_filename
import os

from ..models import Image 
from ..utils import get_images_by_place, get_images_by_user, create_image, delete_image
from .. import db


class ImageConverter(BaseConverter):
    def to_python(self, value):
        db_image = Image.query.filter_by(id=value).first()
        if db_image is None:
            raise NotFound
        return db_image
        
    def to_url(self, value):
        return str(value.id)

class ImageCollection(Resource):
#    def get(self):
  #      """Get all images with optional filtering"""
   #     trust_score = request.args.get("trust_score", 0, type=float)
    #    imagepath = request.args.get("imagepath", None, type=str)
     #   description = request.args.get("description", None, type=str)
      #  timestamp = request.args.get("timestamp", None, type=datetime)
       # application = request.args.get("application", None, type=str)

    def post(self):
        """Upload and create a new image"""
        if 'file' not in request.files:
            return {"error": "No file provided"}, 400

        file = request.files['file']

        if file.filename == '':
            return {"error": "Empty filename"}, 400
        
        filename = secure_filename(file.filename)

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        image = create_image(
            user_id=request.form.get("user_id"),
            place_id=request.form.get("place_id"),
            image_path=f"uploads/{filename}",
            description=request.form.get("description")
        )

        return {
            "id": image.id,
            "message": "Image uploaded successfully"
        }, 201

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
