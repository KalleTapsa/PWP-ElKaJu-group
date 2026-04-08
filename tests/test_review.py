import pytest

from PeculiarPlaces.models import Place, Review, User


@pytest.mark.integration
def test_get_reviews_empty(session, client):
    """Test GET /api/places/<id>/reviews/ for place with no reviews."""
    user = User(api_key="test_get_reviews_empty")
    session.add(user)
    session.commit()

    place = Place(
        name="Test Place",
        description="Desc",
        latitude=0.0,
        longitude=0.0,
        user_id=user.id,
    )
    session.add(place)
    session.commit()

    response = client.get(f"/api/places/{place.id}/reviews/")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.integration
def test_create_review(session, client):
    """Test POST /api/places/<id>/reviews/ creates a review."""
    user = User(api_key="test_create_review")
    session.add(user)
    session.commit()

    place = Place(
        name="Test Place",
        description="Desc",
        latitude=0.0,
        longitude=0.0,
        user_id=user.id,
    )
    session.add(place)
    session.commit()

    response = client.post(
        f"/api/places/{place.id}/reviews/",
        json={"rating": 5, "text": "Great place!"},
        headers={"Authorization": "test_create_review"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Review created successfully"
    assert "id" in data


@pytest.mark.integration
def test_create_review_unauthorized(client):
    """Test POST /api/places/<id>/reviews/ without auth fails."""
    response = client.post(
        "/api/places/1/reviews/",
        json={"rating": 5, "text": "Great place!"},
    )
    assert response.status_code == 401


@pytest.mark.integration
def test_create_review_invalid_rating(session, client):
    """Test POST /api/places/<id>/reviews/ with invalid rating."""
    user = User(api_key="test_create_review_invalid_rating")
    session.add(user)
    session.commit()

    place = Place(
        name="Test Place",
        description="Desc",
        latitude=0.0,
        longitude=0.0,
        user_id=user.id,
    )
    session.add(place)
    session.commit()

    response = client.post(
        f"/api/places/{place.id}/reviews/",
        json={"rating": 10, "text": "Invalid rating"},
        headers={"Authorization": "test_create_review_invalid_rating"},
    )
    assert response.status_code == 400


@pytest.mark.integration
def test_create_review_missing_rating(session, client):
    """Test POST /api/places/<id>/reviews/ without required rating field."""
    user = User(api_key="test_create_review_missing_rating")
    session.add(user)
    session.commit()

    place = Place(
        name="Test Place",
        description="Desc",
        latitude=0.0,
        longitude=0.0,
        user_id=user.id,
    )
    session.add(place)
    session.commit()

    response = client.post(
        f"/api/places/{place.id}/reviews/",
        json={"text": "Missing rating"},
        headers={"Authorization": "test_create_review_missing_rating"},
    )
    assert response.status_code == 400


@pytest.mark.integration
def test_get_review_by_id(session, client):
    """Test GET /api/places/<place_id>/reviews/<review_id>/."""
    user = User(api_key="test_get_review_by_id")
    session.add(user)
    session.commit()

    place = Place(
        name="Test Place",
        description="Desc",
        latitude=0.0,
        longitude=0.0,
        user_id=user.id,
    )
    session.add(place)
    session.commit()

    review = Review(rating=4, text="Good place", place_id=place.id, user_id=user.id)
    session.add(review)
    session.commit()

    response = client.get(f"/api/places/{place.id}/reviews/{review.id}/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == review.id
    assert data["rating"] == review.rating
    assert data["text"] == review.text
    assert data["place_id"] == place.id


@pytest.mark.integration
def test_get_review_not_found(client):
    """Test GET /api/places/<place_id>/reviews/<review_id>/ for non-existent review."""
    response = client.get("/api/places/1/reviews/999/")
    assert response.status_code == 404


@pytest.mark.integration
def test_delete_review(session, client):
    """Test DELETE /api/places/<place_id>/reviews/<review_id>/."""
    user = User(api_key="test_delete_review")
    session.add(user)
    session.commit()

    place = Place(
        name="Test Place",
        description="Desc",
        latitude=0.0,
        longitude=0.0,
        user_id=user.id,
    )
    session.add(place)
    session.commit()

    review = Review(rating=4, text="Good place", place_id=place.id, user_id=user.id)
    session.add(review)
    session.commit()

    response = client.delete(
        f"/api/places/{place.id}/reviews/{review.id}/",
        headers={"Authorization": "test_delete_review"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Review deleted successfully"

    # Check deleted
    response = client.get(f"/api/places/{place.id}/reviews/{review.id}/")
    assert response.status_code == 404


@pytest.mark.integration
def test_delete_review_not_owner(session, client):
    """Test DELETE /api/places/<place_id>/reviews/<review_id>/ by non-owner fails."""
    owner = User(api_key="test_delete_review_not_owner")
    session.add(owner)
    session.commit()

    other = User(api_key="test_delete_review_not_owner2")
    session.add(other)
    session.commit()

    place = Place(
        name="Test Place",
        description="Desc",
        latitude=0.0,
        longitude=0.0,
        user_id=owner.id,
    )
    session.add(place)
    session.commit()

    review = Review(rating=4, text="Good place", place_id=place.id, user_id=owner.id)
    session.add(review)
    session.commit()

    response = client.delete(
        f"/api/places/{place.id}/reviews/{review.id}/",
        headers={"Authorization": "test_delete_review_not_owner2"},
    )
    assert response.status_code == 403


@pytest.mark.integration
def test_get_user_reviews(session, client):
    """Test GET /api/users/<user_id>/reviews/."""
    user = User(api_key="test_get_user_reviews")
    session.add(user)
    session.commit()

    place1 = Place(
        name="Place1",
        description="Desc",
        latitude=0.0,
        longitude=0.0,
        user_id=user.id,
    )
    session.add(place1)
    session.commit()

    place2 = Place(
        name="Place2",
        description="Desc",
        latitude=1.0,
        longitude=1.0,
        user_id=user.id,
    )
    session.add(place2)
    session.commit()

    review1 = Review(rating=5, text="Excellent", place_id=place1.id, user_id=user.id)
    session.add(review1)
    session.commit()

    review2 = Review(rating=3, text="Okay", place_id=place2.id, user_id=user.id)
    session.add(review2)
    session.commit()

    response = client.get(f"/api/users/{user.id}/reviews/")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    ratings = [r["rating"] for r in data]
    assert 5 in ratings
    assert 3 in ratings
