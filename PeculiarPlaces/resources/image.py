import os
import uuid

from flask import current_app, g, request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest, NotFound

from ..authentication import login_required, require_ownership
from ..utils import (
    create_image,
    delete_image,
    get_images_by_place,
    get_images_by_user,
    get_place_by_id,
    get_user_by_id,
)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
IMAGE_CACHE = {}


def allowed_file(filename):
    """Check if a filename has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class ImageCollection(Resource):
    """Resource for handling a collection of images for a place."""

    method_decorators = {"get": [], "post": [login_required]}

    def get(self, place_id):
        """Get all images for a specific place"""
        if not get_place_by_id(place_id):
            raise NotFound(description="Place not found")
        if place_id in IMAGE_CACHE:
            return IMAGE_CACHE[place_id], 200

        images = get_images_by_place(place_id)
        res = [
            {
                "id": image.id,
                "user_id": image.user_id,
                "place_id": image.place_id,
                "description": image.description,
                "timestamp": image.timestamp.isoformat(),
                "trust_score": float(image.trust_score),
                "image_url": f"/api/uploads/{image.image_path}",
            }
            for image in images
        ]

        IMAGE_CACHE[place_id] = res

        return res, 200

    def post(self, place_id):
        """Upload and create a new image"""
        if "file" not in request.files:
            return {"error": "No file provided"}, 400

        file = request.files["file"]

        if file.filename is None or file.filename == "":
            return {"error": "Empty filename"}, 400

        if not allowed_file(file.filename):
            return {
                "error": "File type not allowed. Only jpg, jpeg, and png allowed"
            }, 400

        if not get_place_by_id(place_id):
            raise NotFound(description="Place not found")

        user_id = g.current_user.id

        filepath = None
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
                description=request.form.get("description"),
            )

            if place_id in IMAGE_CACHE:
                del IMAGE_CACHE[place_id]

            return {"id": image.id, "message": "Image uploaded successfully"}, 201
        except Exception as e:
            if filepath and os.path.isfile(filepath):
                os.remove(filepath)
            raise BadRequest(description=str(e))


class ImageItem(Resource):
    """Resource for handling a single image."""

    method_decorators = {"get": [], "delete": [login_required]}

    def get(self, place_id, image):
        """Get image metadata including download URL"""
        if image.place_id != place_id:
            raise NotFound(description="Image not found")

        return {
            "id": image.id,
            "user_id": image.user_id,
            "place_id": image.place_id,
            "description": image.description,
            "timestamp": image.timestamp.isoformat(),
            "trust_score": float(image.trust_score),
            "image_url": f"/api/uploads/{image.image_path}",
        }, 200

    def delete(self, place_id, image):
        """Delete an image and its file"""
        if image.place_id != place_id:
            raise NotFound(description="Image not found")

        require_ownership(image.user_id)

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        file_path = os.path.join(upload_folder, image.image_path)
        if os.path.isfile(file_path):
            os.remove(file_path)

        delete_image(image.id)
        if place_id in IMAGE_CACHE:
            del IMAGE_CACHE[place_id]

        return {"message": "Image deleted successfully"}, 200


class ImagesByUser(Resource):
    """Resource for handling images created by a user."""

    method_decorators = {"get": []}

    def get(self, user_id):
        """Get all images by a specific user"""
        if not get_user_by_id(user_id):
            raise NotFound(description="User not found")
        images = get_images_by_user(user_id)
        res = [
            {
                "id": image.id,
                "user_id": image.user_id,
                "place_id": image.place_id,
                "description": image.description,
                "timestamp": image.timestamp.isoformat(),
                "trust_score": float(image.trust_score),
                "image_url": f"/api/uploads/{image.image_path}",
            }
            for image in images
        ]
        return res, 200
