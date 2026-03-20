from flask import Blueprint, send_from_directory, current_app
from flask_restful import Resource, Api
from .resources.place import Places, PlaceItem, PlacesByUser
from .resources.review import ReviewById, PlaceReviews, ReviewsByUser
from .resources.report import (
    ReportPlaceById, AllPlaceReports, ReportPlaceByUser,
    ReportReviewById, AllReviewReports, ReportReviewByUser,
    ReportImageById, AllImageReports, ReportImageByUser
)
from .resources.image import (
    ImageCollection, ImageItem, ImagesByUser
)
from .resources.user import Users

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

# User endpoints
api.add_resource(Users, "/users/", "/users/<int:user_id>/")

# Place endpoints
api.add_resource(Places, "/places/")
api.add_resource(PlaceItem, "/places/<place:place>/")
api.add_resource(PlacesByUser, "/users/<int:user_id>/places/")

# Review endpoints
api.add_resource(PlaceReviews, "/places/<int:place_id>/reviews/")
api.add_resource(ReviewById,"/places/<int:place_id>/reviews/<int:review_id>/")
api.add_resource(ReviewsByUser, "/users/<int:user_id>/reviews/")

# Image endpoints
api.add_resource(ImageCollection,"/places/<int:place_id>/images/")
api.add_resource(ImageItem,"/places/<int:place_id>/images/<int:image_id>/")
api.add_resource(ImagesByUser, "/users/<int:user_id>/images/")

# Report Place endpoints
api.add_resource(AllPlaceReports,"/places/<int:place_id>/reports/")
api.add_resource(ReportPlaceById,"/places/<int:place_id>/reports/<int:report_id>/")
api.add_resource(ReportPlaceByUser,"/users/<int:user_id>/reports/places/")

# Report Review endpoints
api.add_resource(AllReviewReports, "/places/<int:place_id>/reviews/<int:review_id>/reports/")
api.add_resource(ReportReviewById, "/places/<int:place_id>/reviews/<int:review_id>/reports/<int:report_id>/")
api.add_resource(ReportReviewByUser,"/users/<int:user_id>/reports/reviews/")

# Report Image endpoints
api.add_resource(AllImageReports,"/places/<int:place_id>/images/<int:image_id>/reports/")
api.add_resource(ReportImageById, "/places/<int:place_id>/images/<int:image_id>/reports/<int:report_id>/")
api.add_resource(ReportImageByUser, "/users/<int:user_id>/reports/images/")

@api_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

