import pytest

from PeculiarPlaces.models import User


@pytest.mark.integration
def test_require_api_key_valid(client, session):
    """Test that a valid API key allows access to protected endpoints."""
    # Create a user
    user = User(api_key="test_require_api_key_valid")
    session.add(user)
    session.commit()

    print("here", User.query.all())

    # Test POST to places with valid key
    response = client.post(
        "/api/places/",
        json={
            "name": "Test Place",
            "description": "Test",
            "latitude": 0.0,
            "longitude": 0.0,
        },
        headers={"Authorization": "test_require_api_key_valid"},
    )
    print(response.json)
    assert response.status_code == 201


@pytest.mark.integration
def test_require_api_key_invalid(client, session):
    """Test that an invalid API key is rejected."""
    user = User(api_key="test_require_api_key_invalid")
    session.add(user)
    session.commit()

    response = client.post(
        "/api/places/",
        json={
            "name": "Test Place",
            "description": "Test",
            "latitude": 0.0,
            "longitude": 0.0,
        },
        headers={"Authorization": "invalidkey"},
    )
    assert response.status_code == 401


@pytest.mark.integration
def test_require_api_key_missing(client, session):
    """Test that missing API key is rejected."""
    user = User(api_key="test_require_api_key_missing")
    session.add(user)
    session.commit()

    response = client.post(
        "/api/places/",
        json={
            "name": "Test Place",
            "description": "Test",
            "latitude": 0.0,
            "longitude": 0.0,
        },
    )
    assert response.status_code == 401
