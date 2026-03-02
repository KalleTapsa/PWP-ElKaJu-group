from flask import Blueprint, send_from_directory, current_app
from flask_restful import Resource, Api
from .resources.place import PlaceCollection, PlaceItem, PlacesByUser
from .resources.review import ReviewCollection, ReviewById, AllPlaceReviews, ReviewsByUser
from .resources.report import (
    ReportPlaceCollection, ReportPlaceById, AllPlaceReports, ReportPlaceByUser,
    ReportReviewCollection, ReportReviewById, AllReviewReports, ReportReviewByUser,
    ReportImageCollection, ReportImageById, AllImageReports, ReportImageByUser
)
from .resources.image import (
    ImageCollection, ImageItem, ImagesByUser, ImagesByPlace
)

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

# Place endpoints
api.add_resource(PlaceCollection, "/places/")
api.add_resource(PlaceItem, "/places/<place:place>/")
api.add_resource(PlacesByUser, "/users/<int:user_id>/places/")

# Review endpoints
api.add_resource(ReviewCollection, "/reviews/")
api.add_resource(ReviewById, "/reviews/<int:review_id>/")
api.add_resource(AllPlaceReviews, "/places/<int:place_id>/reviews/")
api.add_resource(ReviewsByUser, "/users/<int:user_id>/reviews/")

# Image endpoints
api.add_resource(ImageCollection, "/images/")
api.add_resource(ImageItem, "/images/<image:image>/")
api.add_resource(ImagesByUser, "/users/<int:user_id>/images/")
api.add_resource(ImagesByPlace, "/places/<int:place_id>/images/")

# Report Place endpoints
api.add_resource(ReportPlaceCollection, "/reports/places/")
api.add_resource(ReportPlaceById, "/reports/places/<int:report_id>/")
api.add_resource(AllPlaceReports, "/places/<int:place_id>/reports/")
api.add_resource(ReportPlaceByUser, "/users/<int:user_id>/reports/places/")

# Report Review endpoints
api.add_resource(ReportReviewCollection, "/reports/reviews/")
api.add_resource(ReportReviewById, "/reports/reviews/<int:report_id>/")
api.add_resource(AllReviewReports, "/reviews/<int:review_id>/reports/")
api.add_resource(ReportReviewByUser, "/users/<int:user_id>/reports/reviews/")

# Report Image endpoints
api.add_resource(ReportImageCollection, "/reports/images/")
api.add_resource(ReportImageById, "/reports/images/<int:report_id>/")
api.add_resource(AllImageReports, "/images/<int:image_id>/reports/")
api.add_resource(ReportImageByUser, "/users/<int:user_id>/reports/images/")

@api_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

