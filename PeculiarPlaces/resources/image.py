from datetime import datetime
import uuid
from flask import request, current_app, g
from flask_restful import Api, Resource
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound, BadRequest
from werkzeug.utils import secure_filename
from ..authentication import require_api_key, require_ownership
from ..utils import (
    get_images_by_place, get_images_by_user, create_image, delete_image, get_image_by_id
)
import os

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

class ImageCollection(Resource):
    method_decorators = {
        "get": [],
        "post": [require_api_key]
    }

    def get(self, place_id):
        """Get all images for a specific place"""
        images = get_images_by_place(place_id)
        res = [
            {
                "id": image.id,
                "user_id": image.user_id,
                "place_id": image.place_id,
                "description": image.description,
                "timestamp": image.timestamp.isoformat(),
                "trust_score": float(image.trust_score),
                "image_url": f"/api/uploads/{image.image_path}"
            } for image in images
        ]
        return res, 200

    def post(self):
        """Upload and create a new image"""
        if 'file' not in request.files:
            return {"error": "No file provided"}, 400

        file = request.files['file']

        if file.filename == '':
            return {"error": "Empty filename"}, 400

        if not allowed_file(file.filename):
            return {"error": "File type not allowed. Only jpg, jpeg, and png allowed"}, 400
        

        place_id = request.form.get("place_id")

        if not g.current_user or not place_id:
            raise BadRequest(description="Missing required fields: 'user_id' and 'place_id'")

        user_id = g.current_user.id

        try:
            ext = file.filename.rsplit(".", 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{ext}"

            upload_folder = current_app.config["UPLOAD_FOLDER"]
            filepath = os.path.join(upload_folder, unique_filename)
            file.save(filepath)

            image = create_image(
                user_id=user_id,
                place_id=place_id,
                image_path=unique_filename,
                description=request.form.get("description")
            )

            return {
                "id": image.id,
                "message": "Image uploaded successfully"
            }, 201
        except Exception as e:
            if os.path.isfile(filepath):
                os.remove(filepath)
            raise BadRequest(description=str(e))

class ImageItem(Resource):
    method_decorators = {
        "get": [],
        "delete": [require_api_key]
    }

    def get(self, image):
        """Get image metadata including download URL"""
        image = get_image_by_id(image.id)
        if not image:
            raise NotFound(description="Image not found")
        
        return {
            "id": image.id,
            "user_id": image.user_id,
            "place_id": image.place_id,
            "description": image.description,
            "timestamp": image.timestamp.isoformat(),
            "trust_score": float(image.trust_score),
            "image_url": f"/api/uploads/{image.image_path}"
        }, 200

    def delete(self, image):
        """Delete an image and its file"""
        image = get_image_by_id(image.id)
        if not image:
            raise NotFound(description="Image not found")
        
        require_ownership(image.user_id)

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        file_path = os.path.join(upload_folder, image.image_path)
        if os.path.isfile(file_path):
            os.remove(file_path)

        delete_image(image.id)
        return {"message": "Image deleted successfully"}, 200

class ImagesByUser(Resource):
    method_decorators = {
        "get": []
    }

    def get(self, user_id):
        """Get all images by a specific user"""
        images = get_images_by_user(user_id)
        res = [
            {
                "id": image.id,
                "user_id": image.user_id,
                "place_id": image.place_id,
                "description": image.description,
                "timestamp": image.timestamp.isoformat(),
                "trust_score": float(image.trust_score),
                "image_url": f"/api/uploads/{image.image_path}"
            } for image in images
        ]
        return res, 200
