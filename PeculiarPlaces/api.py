from flask import Blueprint
from flask_restful import Resource, Api
from models import app, db
from resources.place import PlaceCollection, PlaceItem, PlacesByUser
from resources.review import ReviewCollection, ReviewById, AllPlaceReviews, ReviewsByUser
from resources.report import (
    ReportPlaceCollection, ReportPlaceById, AllPlaceReports, ReportPlaceByUser,
    ReportReviewCollection, ReportReviewById, AllReviewReports, ReportReviewByUser,
    ReportImageCollection, ReportImageById, AllImageReports, ReportImageByUser
)
api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

# Place endpoints
api.add_resource(PlaceCollection, "/api/places/")
api.add_resource(PlaceItem, "/api/places/<place:place>/")
api.add_resource(PlacesByUser, "/api/users/<int:user_id>/places/")

# Review endpoints
api.add_resource(ReviewCollection, "/api/reviews/")
api.add_resource(ReviewById, "/api/reviews/<int:review_id>/")
api.add_resource(AllPlaceReviews, "/api/places/<int:place_id>/reviews/")
api.add_resource(ReviewsByUser, "/api/users/<int:user_id>/reviews/")

# Report Place endpoints
api.add_resource(ReportPlaceCollection, "/api/reports/places/")
api.add_resource(ReportPlaceById, "/api/reports/places/<int:report_id>/")
api.add_resource(AllPlaceReports, "/api/places/<int:place_id>/reports/")
api.add_resource(ReportPlaceByUser, "/api/users/<int:user_id>/reports/places/")

# Report Review endpoints
api.add_resource(ReportReviewCollection, "/api/reports/reviews/")
api.add_resource(ReportReviewById, "/api/reports/reviews/<int:report_id>/")
api.add_resource(AllReviewReports, "/api/reviews/<int:review_id>/reports/")
api.add_resource(ReportReviewByUser, "/api/users/<int:user_id>/reports/reviews/")

# Report Image endpoints
api.add_resource(ReportImageCollection, "/api/reports/images/")
api.add_resource(ReportImageById, "/api/reports/images/<int:report_id>/")
api.add_resource(AllImageReports, "/api/images/<int:image_id>/reports/")
api.add_resource(ReportImageByUser, "/api/users/<int:user_id>/reports/images/")

