"""
Pytest configuration and fixtures for the PeculiarPlaces application.
"""

# pylint: disable=redefined-outer-name
import factory
import pytest
from factory.alchemy import SQLAlchemyModelFactory


from PeculiarPlaces import create_app, db
from PeculiarPlaces.models import (
    Image,
    Place,
    Review,
    User,
)


@pytest.fixture(scope="session")
def app():
    """Create and configure a test app instance."""
    app_instance = create_app()
    app_instance.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )
    return app_instance


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
    # transaction = connection.begin()

    options = {"bind": connection, "binds": {}}
    db_session = _db.create_session(**options)

    yield db_session

    # transaction.rollback()
    connection.close()
    db_session.close()


@pytest.fixture(scope="function")
def client(app):
    """A test client for the app."""
    return app.test_client()


# Factory-boy factories
class UserFactory(SQLAlchemyModelFactory):
    """Factory for User model."""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Meta configuration for UserFactory."""

        # pylint: disable=too-few-public-methods
        model = User
        sqlalchemy_session = None  # Will be set in fixture

    api_key = factory.Sequence(lambda n: f"key{n}")


class PlaceFactory(SQLAlchemyModelFactory):
    """Factory for Place model."""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Meta configuration for PlaceFactory."""

        # pylint: disable=too-few-public-methods
        model = Place
        sqlalchemy_session = None

    name = factory.Sequence(lambda n: f"Place {n}")
    description = "A peculiar place"
    latitude = factory.Faker("latitude")
    longitude = factory.Faker("longitude")
    user_id = factory.SubFactory(UserFactory)


class ReviewFactory(SQLAlchemyModelFactory):
    """Factory for Review model."""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Meta configuration for ReviewFactory."""

        # pylint: disable=too-few-public-methods
        model = Review
        sqlalchemy_session = None

    rating = 5
    text = "Great place!"
    place_id = factory.SubFactory(PlaceFactory)
    user_id = factory.SubFactory(UserFactory)


class ImageFactory(SQLAlchemyModelFactory):
    """Factory for Image model."""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Meta configuration for ImageFactory."""

        # pylint: disable=too-few-public-methods
        model = Image
        sqlalchemy_session = None

    image_path = factory.Sequence(lambda n: f"image{n}.jpg")
    place_id = factory.SubFactory(PlaceFactory)
    user_id = factory.SubFactory(UserFactory)


@pytest.fixture(scope="function", autouse=True)
def set_session_factories(session):
    """Set the session for factories.

    Note: 'session' here is the SQLAlchemy session object yielded from the 'session' fixture.
    """
    # pylint: disable=protected-access
    # Ensure we are setting the session on the factory's meta
    UserFactory._meta.sqlalchemy_session = session
    PlaceFactory._meta.sqlalchemy_session = session
    ReviewFactory._meta.sqlalchemy_session = session
    ImageFactory._meta.sqlalchemy_session = session
