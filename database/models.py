from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

app = Flask(__name__, static_folder="static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///development.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class ReportType(Enum):
    INCORRECT = 1
    INAPPROPRIATE = 2
    APPROPRIATE = 3

REPORT_WEIGHTS = {
    ReportType.APPROPRIATE: 0.4,
    ReportType.INCORRECT: -0.4,
    ReportType.INAPPROPRIATE: -0.8,
}

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    places = db.relationship("Place", back_populates="user")
    reviews = db.relationship("Review", back_populates="user")
    images = db.relationship("Image", back_populates="user")

class Place(db.Model):
    __tablename__ = "places"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=False)

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(512))
    category = db.Column(db.String(64))
    address = db.Column(db.String(255))
    postal_code = db.Column(db.String(32))
    city = db.Column(db.String(64))

    latitude = db.Column(db.Numeric(9, 6), nullable=False)
    longitude = db.Column(db.Numeric(9, 6), nullable=False)

    application = db.Column(db.String(64))
    trust_score = db.Column(db.Numeric, default=4.0)

    user = db.relationship("User", back_populates="places")
    reviews = db.relationship("Review", back_populates="place")
    images = db.relationship("Image", back_populates="place")

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey("places.id", ondelete="CASCADE"), nullable=False)

    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(512))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(datetime.timezone.utc))
    trust_score = db.Column(db.Numeric, default=4.0)

    user = db.relationship("User", back_populates="reviews")
    place = db.relationship("Place", back_populates="reviews")

class Image(db.Model):
    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey("places.id", ondelete="CASCADE"), nullable=False)

    image_path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(512))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(datetime.timezone.utc))
    trust_score = db.Column(db.Numeric, default=4.0)
    
    user = db.relationship("User", back_populates="images")
    place = db.relationship("Place", back_populates="images")

class ReportPlace(db.Model):
    __tablename__ = "reports_place"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey("places.id", ondelete="CASCADE"), nullable=False)

    report_type = db.Column(db.Enum(ReportType), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(datetime.timezone.utc))

    user = db.relationship("User", back_populates="reports_place")
    place = db.relationship("Place", back_populates="reports_place")

class ReportReview(db.Model):
    __tablename__ = "reports_review"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)

    report_type = db.Column(db.Enum(ReportType), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(datetime.timezone.utc))

    user = db.relationship("User", back_populates="reports_review")
    review = db.relationship("Review", back_populates="reports_review")

class ReportImage(db.Model):
    __tablename__ = "reports_image"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey("images.id", ondelete="CASCADE"), nullable=False)

    report_type = db.Column(db.Enum(ReportType), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(datetime.timezone.utc))

    user = db.relationship("User", back_populates="reports_image")
    image = db.relationship("Image", back_populates="reports_image")

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
    return Image.query.filter(Image.place_id==place_id, Image.trust_score>=trust_score).all()

def get_images_by_user(user_id):
    return Image.query.filter_by(user_id=user_id).all()

def create_image(user_id, place_id, image_path, description=None):
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

def create_report_place(user_id, place_id, report_type):
    report = ReportPlace.query.filter_by(user_id=user_id, place_id=place_id).first()
    if report:
        report.report_type = report_type
        report.timestamp = datetime.now(datetime.timezone.utc)
    else:
        report = ReportPlace(user_id=user_id, place_id=place_id, report_type=report_type)
        db.session.add(report)

    db.session.commit()

    recalculate_place_trust_score(place_id)

    return report

# Report review
def get_report_review_by_id(report_id):
    return ReportReview.query.get(report_id)

def get_report_reviews_by_review(review_id):
    return ReportReview.query.filter_by(review_id=review_id).all()

def get_report_reviews_by_user(user_id):
    return ReportReview.query.filter_by(user_id=user_id).all()

def create_report_review(user_id, review_id, report_type):
    report = ReportReview.query.filter_by(user_id=user_id, review_id=review_id).first()
    if report:
        report.report_type = report_type
        report.timestamp = datetime.now(datetime.timezone.utc)
    else:
        report = ReportReview(user_id=user_id, review_id=review_id, report_type=report_type)
        db.session.add(report)

    db.session.commit()

    recalculate_review_trust_score(review_id)

    return report

# Report image
def get_report_image_by_id(report_id):
    return ReportImage.query.get(report_id)

def get_report_images_by_image(image_id):
    return ReportImage.query.filter_by(image_id=image_id).all()

def get_report_images_by_user(user_id):
    return ReportImage.query.filter_by(user_id=user_id).all()

def create_report_image(user_id, image_id, report_type):
    report = ReportImage.query.filter_by(user_id=user_id, image_id=image_id).first()
    if report:
        report.report_type = report_type
        report.timestamp = datetime.now(datetime.timezone.utc)
    else:
        report = ReportImage(user_id=user_id, image_id=image_id, report_type=report_type)
        db.session.add(report)

    db.session.commit()

    recalculate_image_trust_score(image_id)

    return report

# Trust score functions
def calculate_trust_score(base_score, weights):
    score = float(base_score)
    for weight in weights:
        score += weight
    return max(0.0, min(5.0, score))

def recalculate_place_trust_score(place_id):
    reports = ReportPlace.query.filter_by(place_id=place_id).all()
    weights = [REPORT_WEIGHTS[report.report_type] for report in reports]
    new_score = calculate_trust_score(4.0, weights)
    
    place = Place.query.get(place_id)
    if place:
        place.trust_score = new_score
        db.session.commit()
    return new_score

def recalculate_review_trust_score(review_id):
    """Recalculate trust score for a review based on all its reports."""
    reports = ReportReview.query.filter_by(review_id=review_id).all()
    weights = [REPORT_WEIGHTS[report.report_type] for report in reports]
    new_score = calculate_trust_score(4.0, weights)
    
    review = Review.query.get(review_id)
    if review:
        review.trust_score = new_score
        db.session.commit()
    return new_score

def recalculate_image_trust_score(image_id):
    """Recalculate trust score for an image based on all its reports."""
    reports = ReportImage.query.filter_by(image_id=image_id).all()
    weights = [REPORT_WEIGHTS[report.report_type] for report in reports]
    new_score = calculate_trust_score(4.0, weights)
    
    image = Image.query.get(image_id)
    if image:
        image.trust_score = new_score
        db.session.commit()
    return new_score