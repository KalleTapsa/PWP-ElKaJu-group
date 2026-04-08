from datetime import datetime, timezone
from enum import Enum
from werkzeug.routing import BaseConverter
from . import db
from werkzeug.exceptions import NotFound
from .models import (
    User, Place, Review, Image,
    ReportPlace, ReportReview, ReportImage
)

class ReportType(Enum):
    INCORRECT = 1
    INAPPROPRIATE = 2
    APPROPRIATE = 3


REPORT_WEIGHTS = {
    ReportType.APPROPRIATE: 0.4,
    ReportType.INCORRECT: -0.4,
    ReportType.INAPPROPRIATE: -0.8,
}

class ImageConverter(BaseConverter):
    def to_python(self, value):
        db_image = Image.query.filter_by(id=value).first()
        if db_image is None:
            raise NotFound
        return db_image
        
    def to_url(self, value):
        return str(value.id)

class PlaceConverter(BaseConverter):
    def to_python(self, value):
        db_place = Place.query.filter_by(id=value).first()
        if db_place is None:
            raise NotFound
        return db_place
        
    def to_url(self, value):
        return str(value.id)

# User
def get_user_by_id(user_id):
    return User.query.get(user_id)

def create_user():
    user = User()
    db.session.add(user)
    db.session.commit()
    return user

# Place
def get_place_by_id(place_id):
    return Place.query.get(place_id)

def get_all_places(trust_score=0, longitude=None, latitude=None, radius=None):
    """Get all places with optional filtering"""
    query = Place.query.filter(Place.trust_score>=trust_score)
    if longitude is not None and latitude is not None and radius is not None:
        query = query.filter(
            (Place.longitude >= longitude - radius) & 
            (Place.longitude <= longitude + radius) & 
            (Place.latitude >= latitude - radius) & 
            (Place.latitude <= latitude + radius)
        )
    return query.all()

def get_places_by_user(user_id):
    return Place.query.filter_by(user_id=user_id).all()

def get_places_by_category(category, trust_score=0, longitude=None, latitude=None, radius=None):
    """Get places by category with optional filtering"""
    query = Place.query.filter(Place.category==category, Place.trust_score>=trust_score)
    if longitude is not None and latitude is not None and radius is not None:
        query = query.filter(
            (Place.longitude >= longitude - radius) & 
            (Place.longitude <= longitude + radius) & 
            (Place.latitude >= latitude - radius) & 
            (Place.latitude <= latitude + radius)
        )
    return query.all()

def get_places_by_application(application, trust_score=0, longitude=None, latitude=None, radius=None):
    """Get places by application with optional filtering"""
    query = Place.query.filter(Place.application==application, Place.trust_score>=trust_score)
    if longitude is not None and latitude is not None and radius is not None:
        query = query.filter(
            (Place.longitude >= longitude - radius) & 
            (Place.longitude <= longitude + radius) & 
            (Place.latitude >= latitude - radius) & 
            (Place.latitude <= latitude + radius)
        )
    return query.all()

def create_place(user_id, name, latitude, longitude, description=None, category=None, address=None, postal_code=None, city=None, application=None):
    """Create a new place with trust_score initialized to 4.0 and only name, latitude and longitude as required fields"""
    place = Place(user_id=user_id, name=name, latitude=latitude, longitude=longitude, 
                  description=description, category=category, address=address, 
                  postal_code=postal_code, city=city, application=application, trust_score=4.0)
    db.session.add(place)
    db.session.commit()
    return place

def delete_place(place_id):
    place = Place.query.get(place_id)
    if place:
        db.session.delete(place)
        db.session.commit()

# Review
def get_review_by_id(review_id):
    return Review.query.get(review_id)

def get_reviews_by_place(place_id, trust_score=0):
    return Review.query.filter(Review.place_id==place_id, Review.trust_score>=trust_score).all()

def get_reviews_by_user(user_id):
    return Review.query.filter_by(user_id=user_id).all()

def create_review(user_id, place_id, rating, text=None):
    """Create a new review with trust_score initialized to 4.0 and only rating as required field"""
    review = Review(user_id=user_id, place_id=place_id, rating=rating, text=text, trust_score=4.0)
    db.session.add(review)
    db.session.commit()
    return review

def delete_review(review_id):
    review = Review.query.get(review_id)
    if review:
        db.session.delete(review)
        db.session.commit()

# Image
def get_image_by_id(image_id):
    return Image.query.get(image_id)

def get_images_by_place(place_id, trust_score=0):
    """Get all images for a specific place with optional trust score filtering"""
    return Image.query.filter(Image.place_id==place_id, Image.trust_score>=trust_score).all()

def get_images_by_user(user_id):
    return Image.query.filter_by(user_id=user_id).all()

def create_image(user_id, place_id, image_path, description=None):
    """Create a new image with trust_score initialized to 4.0"""
    image = Image(user_id=user_id, place_id=place_id, image_path=image_path, description=description, trust_score=4.0)
    db.session.add(image)
    db.session.commit()
    return image

def delete_image(image_id):
    image = Image.query.get(image_id)
    if image:
        db.session.delete(image)
        db.session.commit()

# Report place
def get_report_place_by_id(report_id):
    return ReportPlace.query.get(report_id)

def get_report_places_by_place(place_id):
    return ReportPlace.query.filter_by(place_id=place_id).all()

def get_report_places_by_user(user_id):
    return ReportPlace.query.filter_by(user_id=user_id).all()

def create_report_place(user_id, place_id, report_type: ReportType):
    """Create or update a report for a place by a user"""
    report_value = report_type.value

    report = ReportPlace.query.filter_by(user_id=user_id, place_id=place_id).first()
    if report:
        report.report_type = report_value
        report.timestamp = datetime.now(timezone.utc)
    else:
        report = ReportPlace(
            user_id=user_id,
            place_id=place_id,
            report_type=report_value
        )
        db.session.add(report)

    db.session.commit()
    recalculate_place_trust_score(place_id)
    return report

def change_report_place(report_id, report_type: ReportType):
    """Change the report type of an existing place report"""
    report_value = report_type.value

    report = ReportPlace.query.get(report_id)
    if report:
        report.report_type = report_value
        report.timestamp = datetime.now(timezone.utc)
        db.session.commit()
        recalculate_place_trust_score(report.place_id)
    return report

# Report review
def get_report_review_by_id(report_id):
    return ReportReview.query.get(report_id)

def get_report_reviews_by_review(review_id):
    return ReportReview.query.filter_by(review_id=review_id).all()

def get_report_reviews_by_user(user_id):
    return ReportReview.query.filter_by(user_id=user_id).all()

def create_report_review(user_id, review_id, report_type: ReportType):
    """Create or update a report for a review by a user"""
    report_value = report_type.value

    report = ReportReview.query.filter_by(user_id=user_id, review_id=review_id).first()
    if report:
        report.report_type = report_value
        report.timestamp = datetime.now(timezone.utc)
    else:
        report = ReportReview(
            user_id=user_id,
            review_id=review_id,
            report_type=report_value
        )
        db.session.add(report)

    db.session.commit()
    recalculate_review_trust_score(review_id)
    return report

def change_report_review(report_id, report_type: ReportType):
    """Change the report type of an existing review report"""
    report_value = report_type.value

    report = ReportReview.query.get(report_id)
    if report:
        report.report_type = report_value
        report.timestamp = datetime.now(timezone.utc)
        db.session.commit()
        recalculate_review_trust_score(report.review_id)
    return report

# Report image
def get_report_image_by_id(report_id):
    return ReportImage.query.get(report_id)

def get_report_images_by_image(image_id):
    return ReportImage.query.filter_by(image_id=image_id).all()

def get_report_images_by_user(user_id):
    return ReportImage.query.filter_by(user_id=user_id).all()

def create_report_image(user_id, image_id, report_type: ReportType):
    """Create or update a report for an image by a user"""
    report_value = report_type.value

    report = ReportImage.query.filter_by(user_id=user_id, image_id=image_id).first()
    if report:
        report.report_type = report_value
        report.timestamp = datetime.now(timezone.utc)
    else:
        report = ReportImage(
            user_id=user_id,
            image_id=image_id,
            report_type=report_value
        )
        db.session.add(report)

    db.session.commit()
    recalculate_image_trust_score(image_id)
    return report

def change_report_image(report_id, report_type: ReportType):
    """Change the report type of an existing image report"""
    report_value = report_type.value

    report = ReportImage.query.get(report_id)
    if report:
        report.report_type = report_value
        report.timestamp = datetime.now(timezone.utc)
        db.session.commit()
        recalculate_image_trust_score(report.image_id)
    return report

# Trust score functions
def calculate_trust_score(base_score, weights):
    """Calculate the new trust score based on the base score and the weights of the reports"""
    score = float(base_score)
    for weight in weights:
        score += weight
    return max(0.0, min(5.0, score))

def recalculate_place_trust_score(place_id):
    """Recalculate the trust score of a place based on its reports"""
    reports = ReportPlace.query.filter_by(place_id=place_id).all()
    weights = [
        REPORT_WEIGHTS[ReportType(report.report_type)]
        for report in reports
    ]

    new_score = calculate_trust_score(4.0, weights)

    place = Place.query.get(place_id)
    if place:
        place.trust_score = new_score
        db.session.commit()

    return new_score

def recalculate_review_trust_score(review_id):
    """Recalculate the trust score of a review based on its reports"""
    reports = ReportReview.query.filter_by(review_id=review_id).all()
    weights = [
        REPORT_WEIGHTS[ReportType(report.report_type)]
        for report in reports
    ]

    new_score = calculate_trust_score(4.0, weights)

    review = Review.query.get(review_id)
    if review:
        review.trust_score = new_score
        db.session.commit()

    return new_score
def recalculate_image_trust_score(image_id):
    """Recalculate the trust score of an image based on its reports"""
    reports = ReportImage.query.filter_by(image_id=image_id).all()
    weights = [
        REPORT_WEIGHTS[ReportType(report.report_type)]
        for report in reports
    ]

    new_score = calculate_trust_score(4.0, weights)

    image = Image.query.get(image_id)
    if image:
        image.trust_score = new_score
        db.session.commit()

    return new_score