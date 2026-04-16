import pytest
from sqlalchemy.exc import IntegrityError

from PeculiarPlaces.models import (
    Image,
    Place,
    ReportPlace,
    Review,
    User,
)


@pytest.mark.unit
def test_user_relationships(session):
    """Test User model relationships."""
    # Add random api key for uniqueness
    user = User(api_key="test_user_relationships")
    session.add(user)
    session.commit()
    place = Place(
        name="Place", description="Desc", latitude=0.0, longitude=0.0, user_id=user.id
    )
    session.add(place)
    session.commit()
    review = Review(rating=5, text="Good", place_id=place.id, user_id=user.id)
    session.add(review)
    session.commit()
    image = Image(image_path="img.jpg", place_id=place.id, user_id=user.id)

    session.add(image)
    session.commit()

    assert len(user.places) == 1
    assert len(user.reviews) == 1
    assert len(user.images) == 1


@pytest.mark.unit
def test_report_unique_constraint(session):
    """Test unique constraint on reports."""
    user = User(api_key="test_report_unique_constraint")
    session.add(user)
    session.commit()
    place = Place(
        name="Place", description="Desc", latitude=0.0, longitude=0.0, user_id=user.id
    )
    session.add_all([place])
    session.commit()

    report1 = ReportPlace(user_id=user.id, place_id=place.id, report_type=1)
    session.add(report1)
    session.commit()

    # Try to add another report for same user and place
    report2 = ReportPlace(user_id=user.id, place_id=place.id, report_type=2)
    session.add(report2)
    with pytest.raises(IntegrityError):
        session.commit()


@pytest.mark.unit
def test_trust_score_defaults(session):
    """Test trust score defaults."""
    user = User(api_key="test_trust_score_defaults")
    place = Place(
        name="Place", description="Desc", latitude=0.0, longitude=0.0, user_id=user.id
    )
    session.add_all([user, place])
    session.commit()

    assert place.trust_score == 4.0

    review = Review(rating=5, text="Good", place_id=place.id, user_id=user.id)
    image = Image(image_path="img.jpg", place_id=place.id, user_id=user.id)
    session.add_all([review, image])
    session.commit()

    assert review.trust_score == 4.0
    assert image.trust_score == 4.0


@pytest.mark.unit
def test_trust_score_bounds(session):
    """Test trust score bounds (assuming 0.0 to 5.0)."""
    user = User(api_key="test_trust_score_bounds")
    place = Place(
        name="Place",
        description="Desc",
        latitude=0.0,
        longitude=0.0,
        user_id=user.id,
        trust_score=5.0,
    )
    session.add_all([user, place])
    session.commit()

    assert place.trust_score == 5.0
