from datetime import datetime, timezone

import click
from flask.cli import with_appcontext
from sqlalchemy import event
from sqlalchemy.engine import Engine

from . import db

# Course example API used as a template for the file

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key support in SQLite."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class User(db.Model):
    """User model representing a person who can create places, reviews, and images."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    places = db.relationship("Place", back_populates="user")
    reviews = db.relationship(
        "Review", cascade="all, delete-orphan", back_populates="user"
    )
    images = db.relationship(
        "Image", cascade="all, delete-orphan", back_populates="user"
    )
    reports_place = db.relationship(
        "ReportPlace", cascade="all, delete-orphan", back_populates="user"
    )
    reports_review = db.relationship(
        "ReportReview", cascade="all, delete-orphan", back_populates="user"
    )
    reports_image = db.relationship(
        "ReportImage", cascade="all, delete-orphan", back_populates="user"
    )


class Place(db.Model):
    """Place model representing a peculiar place."""

    __tablename__ = "places"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(512))
    category = db.Column(db.String(64))
    address = db.Column(db.String(255))
    postal_code = db.Column(db.String(32))
    city = db.Column(db.String(64))

    latitude = db.Column(db.Numeric(9, 6), nullable=False)
    longitude = db.Column(db.Numeric(9, 6), nullable=False)

    application = db.Column(db.String(64))
    trust_score = db.Column(db.Numeric(4, 3), default=4.0)

    user = db.relationship("User", back_populates="places")
    reviews = db.relationship(
        "Review", cascade="all, delete-orphan", back_populates="place"
    )
    images = db.relationship(
        "Image", cascade="all, delete-orphan", back_populates="place"
    )

    reports_place = db.relationship(
        "ReportPlace", cascade="all, delete-orphan", back_populates="place"
    )


class Review(db.Model):
    """Review model representing a review of a place."""

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    place_id = db.Column(
        db.Integer, db.ForeignKey("places.id", ondelete="CASCADE"), nullable=False
    )

    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(512))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    trust_score = db.Column(db.Numeric(4, 3), default=4.0)

    user = db.relationship("User", back_populates="reviews")
    place = db.relationship("Place", back_populates="reviews")

    reports_review = db.relationship(
        "ReportReview", cascade="all, delete-orphan", back_populates="review"
    )


class Image(db.Model):
    """Image model representing an image of a place."""

    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    place_id = db.Column(
        db.Integer, db.ForeignKey("places.id", ondelete="CASCADE"), nullable=False
    )

    image_path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(512))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    trust_score = db.Column(db.Numeric(4, 3), default=4.0)

    user = db.relationship("User", back_populates="images")
    place = db.relationship("Place", back_populates="images")

    reports_image = db.relationship(
        "ReportImage", cascade="all, delete-orphan", back_populates="image"
    )


class ReportPlace(db.Model):
    """ReportPlace model representing a report against a place."""

    __tablename__ = "reports_place"
    __table_args__ = (
        db.UniqueConstraint("user_id", "place_id"),
        db.CheckConstraint("report_type IN (1, 2, 3)", name="check_report_place_type"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    place_id = db.Column(
        db.Integer, db.ForeignKey("places.id", ondelete="CASCADE"), nullable=False
    )

    report_type = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="reports_place")
    place = db.relationship("Place", back_populates="reports_place")


class ReportReview(db.Model):
    """ReportReview model representing a report against a review."""

    __tablename__ = "reports_review"
    __table_args__ = (
        db.UniqueConstraint("user_id", "review_id"),
        db.CheckConstraint("report_type IN (1, 2, 3)", name="check_report_review_type"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    review_id = db.Column(
        db.Integer, db.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False
    )

    report_type = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="reports_review")
    review = db.relationship("Review", back_populates="reports_review")


class ReportImage(db.Model):
    """ReportImage model representing a report against an image."""

    __tablename__ = "reports_image"
    __table_args__ = (
        db.UniqueConstraint("user_id", "image_id"),
        db.CheckConstraint("report_type IN (1, 2, 3)", name="check_report_image_type"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    image_id = db.Column(
        db.Integer, db.ForeignKey("images.id", ondelete="CASCADE"), nullable=False
    )

    report_type = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="reports_image")
    image = db.relationship("Image", back_populates="reports_image")


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Flask CLI command to initialize the database."""
    db.create_all()
