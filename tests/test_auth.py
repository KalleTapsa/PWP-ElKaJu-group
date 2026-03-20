import pytest
from PeculiarPlaces.models import User


def test_require_api_key_valid(client, session):
    """Test that a valid API key allows access to protected endpoints."""
    # Create a user
    user = User(api_key="validkey")
    session.add(user)
    session.commit()

    # Test POST to places with valid key
    response = client.post('/api/places/', 
                          json={"name": "Test Place", "description": "Test", "latitude": 0.0, "longitude": 0.0},
                          headers={"X-API-Key": "validkey"})
    assert response.status_code == 201


def test_require_api_key_invalid(client, session):
    """Test that an invalid API key is rejected."""
    response = client.post('/api/places/', 
                          json={"name": "Test Place", "description": "Test", "latitude": 0.0, "longitude": 0.0},
                          headers={"X-API-Key": "invalidkey"})
    assert response.status_code == 401


def test_require_api_key_missing(client):
    """Test that missing API key is rejected."""
    response = client.post('/api/places/', 
                          json={"name": "Test Place", "description": "Test", "latitude": 0.0, "longitude": 0.0})
    assert response.status_code == 401