import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import factory
from factory.alchemy import SQLAlchemyModelFactory

from PeculiarPlaces import create_app, db
from PeculiarPlaces.models import User, Place, Review, Image, ReportPlace, ReportReview, ReportImage


@pytest.fixture(scope="session")
def app():
    """Create and configure a test app instance."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })
    return app


@pytest.fixture(scope="session")
def _db(app):
    """Provide the database object."""
    with app.app_context():
        db.create_all()
    yield db
    with app.app_context():
        db.drop_all()


@pytest.fixture(scope="function")
def session(_db):
    """Create a new database session for a test."""
    connection = _db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    db_session = _db.create_session(**options)

    yield db_session

    transaction.rollback()
    connection.close()
    db_session.close()


@pytest.fixture(scope="function")
def client(app, session):
    """A test client for the app."""
    return app.test_client()


# Factory-boy factories
class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = None  # Will be set in fixture

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    api_key = factory.Sequence(lambda n: f"key{n}")


class PlaceFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Place
        sqlalchemy_session = None

    name = factory.Sequence(lambda n: f"Place {n}")
    description = "A peculiar place"
    latitude = factory.Faker("latitude")
    longitude = factory.Faker("longitude")
    user_id = factory.SubFactory(UserFactory)


class ReviewFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Review
        sqlalchemy_session = None

    rating = 5
    comment = "Great place!"
    place_id = factory.SubFactory(PlaceFactory)
    user_id = factory.SubFactory(UserFactory)


class ImageFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Image
        sqlalchemy_session = None

    filename = factory.Sequence(lambda n: f"image{n}.jpg")
    place_id = factory.SubFactory(PlaceFactory)
    user_id = factory.SubFactory(UserFactory)


@pytest.fixture(scope="function", autouse=True)
def set_session_factories(session):
    """Set the session for factories.
    
    Note: 'session' here is the SQLAlchemy session object yielded from the 'session' fixture.
    """
    # Ensure we are setting the session on the factory's meta
    UserFactory._meta.sqlalchemy_session = session
    PlaceFactory._meta.sqlalchemy_session = session
    ReviewFactory._meta.sqlalchemy_session = session
    ImageFactory._meta.sqlalchemy_session = session
