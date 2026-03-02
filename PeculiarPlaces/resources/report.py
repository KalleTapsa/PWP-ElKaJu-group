from flask import request, jsonify, make_response
from flask_restful import Resource
from werkzeug.exceptions import NotFound, BadRequest
from ..utils import (
    ReportType,
    get_report_place_by_id, get_report_places_by_place, get_report_places_by_user,
    get_report_review_by_id, get_report_reviews_by_review, get_report_reviews_by_user,
    get_report_image_by_id, get_report_images_by_image, get_report_images_by_user,
    create_report_place, create_report_review, create_report_image
)

# Report Place Resources
class ReportPlaceById(Resource):
    def get(self, report_id):
        """Get a specific place report by its ID"""
        report = get_report_place_by_id(report_id)
        if not report:
            raise NotFound(description="Place report not found")
        return {
            "id": report.id,
            "user_id": report.user_id,
            "place_id": report.place_id,
            "report_type": report.report_type,
            "timestamp": report.timestamp.isoformat()
        }, 200

class AllPlaceReports(Resource):
    def get(self, place_id):
        """Get all reports for a specific place"""
        reports = get_report_places_by_place(place_id)
        res = [
            {
                "id": report.id,
                "user_id": report.user_id,
                "place_id": report.place_id,
                "report_type": report.report_type,
                "timestamp": report.timestamp.isoformat()
            } for report in reports
        ]
        return res, 200

    def post(self, place_id):
        """Create or update a report for a place"""

        if request.content_type != "application/json":
            return make_response(
                jsonify({"error": "Request content type must be JSON"}),
                415
            )
        # Only user_id and report_type are required, place_id comes from URL
        required_fields = ["user_id", "report_type"]
        if not request.json or not all(field in request.json for field in required_fields):
            raise BadRequest(description=f"Missing required fields: {required_fields}")

        try:
            report_type = ReportType(request.json["report_type"])

            report = create_report_place(
                user_id=request.json["user_id"],
                place_id=place_id,  # comes from URL
                report_type=report_type
            )

            return make_response(
                jsonify({
                    "id": report.id,
                    "message": "Place report created/updated successfully"
                }),
                201
            )

        except ValueError:
            raise BadRequest(description="Invalid report_type. Must be 1 (INCORRECT), 2 (INAPPROPRIATE), or 3 (APPROPRIATE)")
        except Exception as e:
            raise BadRequest(description=str(e))

class ReportPlaceByUser(Resource):
    def get(self, user_id):
        """Get all place reports by a specific user"""
        reports = get_report_places_by_user(user_id)
        res = [
            {
                "id": report.id,
                "user_id": report.user_id,
                "place_id": report.place_id,
                "report_type": report.report_type,
                "timestamp": report.timestamp.isoformat()
            } for report in reports
        ]
        return res, 200

# Report Review Resources
class ReportReviewById(Resource):
    def get(self, report_id):
        """Get a specific review report by its ID"""
        report = get_report_review_by_id(report_id)
        if not report:
            raise NotFound(description="Review report not found")
        return {
            "id": report.id,
            "user_id": report.user_id,
            "review_id": report.review_id,
            "report_type": report.report_type,
            "timestamp": report.timestamp.isoformat()
        }, 200

class AllReviewReports(Resource):
    def get(self, review_id):
        """Get all reports for a specific review"""
        reports = get_report_reviews_by_review(review_id)
        res = [
            {
                "id": report.id,
                "user_id": report.user_id,
                "review_id": report.review_id,
                "report_type": report.report_type,
                "timestamp": report.timestamp.isoformat()
            } for report in reports
        ]
        return res, 200

    def post(self, place_id, review_id):
        """Create or update a report for a review"""

        if request.content_type != "application/json":
            return make_response(
                jsonify({"error": "Request content type must be JSON"}),
                415
            )

        # Only user_id and report_type are required; place_id/review_id come from URL
        required_fields = ["user_id", "report_type"]
        if not request.json or not all(field in request.json for field in required_fields):
            raise BadRequest(description=f"Missing required fields: {required_fields}")

        try:
            report_type = ReportType(request.json["report_type"])

            # Optional: validate that review belongs to place TODO: This adds an extra DB query, but ensures the review is valid for the place
            #review = get_review_by_id(review_id)
            #if not review or review.place_id != place_id:
             #   raise BadRequest(description="Review not found for this place")

            report = create_report_review(
                user_id=request.json["user_id"],
                review_id=review_id,
                report_type=report_type
            )

            return make_response(
                jsonify({
                    "id": report.id,
                    "message": "Review report created/updated successfully"
                }),
                201
            )

        except ValueError:
            raise BadRequest(description="Invalid report_type. Must be 1 (INCORRECT), 2 (INAPPROPRIATE), or 3 (APPROPRIATE)")
        except Exception as e:
            raise BadRequest(description=str(e))

class ReportReviewByUser(Resource):
    def get(self, user_id):
        """Get all review reports by a specific user"""
        reports = get_report_reviews_by_user(user_id)
        res = [
            {
                "id": report.id,
                "user_id": report.user_id,
                "review_id": report.review_id,
                "report_type": report.report_type,
                "timestamp": report.timestamp.isoformat()
            } for report in reports
        ]
        return res, 200

# Report Image Resources
class ReportImageById(Resource):
    def get(self, report_id):
        """Get a specific image report by its ID"""
        report = get_report_image_by_id(report_id)
        if not report:
            raise NotFound(description="Image report not found")
        return {
            "id": report.id,
            "user_id": report.user_id,
            "image_id": report.image_id,
            "report_type": report.report_type,
            "timestamp": report.timestamp.isoformat()
        }, 200

class AllImageReports(Resource):
    def get(self, image_id):
        """Get all reports for a specific image"""
        reports = get_report_images_by_image(image_id)
        res = [
            {
                "id": report.id,
                "user_id": report.user_id,
                "image_id": report.image_id,
                "report_type": report.report_type,
                "timestamp": report.timestamp.isoformat()
            } for report in reports
        ]
        return res, 200

    def post(self, place_id, image_id):
        """Create or update a report for an image"""

        if request.content_type != "application/json":
            return make_response(
                jsonify({"error": "Request content type must be JSON"}),
                415
            )

        # Only user_id and report_type are required; place_id/image_id come from URL
        required_fields = ["user_id", "report_type"]
        if not request.json or not all(field in request.json for field in required_fields):
            raise BadRequest(description=f"Missing required fields: {required_fields}")

        try:
            report_type = ReportType(request.json["report_type"])

            # Optional: validate that image belongs to place
            image = get_image_by_id(image_id)
            if not image or image.place_id != place_id:
                raise BadRequest(description="Image not found for this place")

            report = create_report_image(
                user_id=request.json["user_id"],
                image_id=image_id,
                report_type=report_type
            )

            return make_response(
                jsonify({
                    "id": report.id,
                    "message": "Image report created/updated successfully"
                }),
                201
            )

        except ValueError:
            raise BadRequest(description="Invalid report_type. Must be 1 (INCORRECT), 2 (INAPPROPRIATE), or 3 (APPROPRIATE)")
        except Exception as e:
            raise BadRequest(description=str(e))

class ReportImageByUser(Resource):
    def get(self, user_id):
        """Get all image reports by a specific user"""
        reports = get_report_images_by_user(user_id)
        res = [
            {
                "id": report.id,
                "user_id": report.user_id,
                "image_id": report.image_id,
                "report_type": report.report_type,
                "timestamp": report.timestamp.isoformat()
            } for report in reports
        ]
        return res, 200