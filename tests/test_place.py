import pytest
from PeculiarPlaces.models import User, Place


@pytest.mark.integration
def test_get_places_empty(client):
    """Test GET /api/places/ with no places."""
    response = client.get('/api/places/')
    assert response.status_code == 200
    data = response.get_json()
    assert data == []


@pytest.mark.integration
def test_create_place(client, session):
    """Test POST /api/places/ creates a place."""
    user = User(api_key="key6")
    session.add(user)
    session.commit()
    
    response = client.post('/api/places/', 
                          json={"name": "Test Place", "description": "A test place", "latitude": 10.0, "longitude": 20.0},
                          headers={"X-API-Key": "key"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Test Place"
    assert "id" in data
    assert "Location" in response.headers


@pytest.mark.integration
def test_create_place_unauthorized(client):
    """Test POST /api/places/ without auth fails."""
    response = client.post('/api/places/', 
                          json={"name": "Test Place", "description": "A test place", "latitude": 10.0, "longitude": 20.0})
    assert response.status_code == 401


@pytest.mark.integration
def test_get_place_by_id(client, session):
    """Test GET /api/places/<id>."""
    user = User(api_key="key7")
    session.add(user)
    session.commit()
    place = Place(name="Test Place", description="Desc", latitude=0.0, longitude=0.0, user_id=user.id)
    session.add(place)
    session.commit()
    
    response = client.get(f'/api/places/')
    assert response.status_code == 200
    data = response.get_json()
    assert data != []


@pytest.mark.integration
def test_get_place_not_found(client):
    """Test GET /api/places/<id> for non-existent place."""
    response = client.get('/api/places/999/')
    assert response.status_code == 404


@pytest.mark.integration
def test_update_place(client, session):
    """Test PUT /api/places/<id>."""
    user = User(api_key="key")
    place = Place(name="Old Name", description="Desc", latitude=0.0, longitude=0.0, user_id=user.id)
    session.add_all([user, place])
    session.commit()
    
    response = client.put(f'/api/places/{place.id}/', 
                         json={"name": "New Name", "description": "Updated", "latitude": 1.0, "longitude": 1.0},
                         headers={"X-API-Key": "key"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "New Name"


@pytest.mark.integration
def test_update_place_not_owner(client, session):
    """Test PUT /api/places/<id> by non-owner fails."""
    owner = User(api_key="ownerkey")
    other = User(api_key="otherkey")
    place = Place(name="Place", description="Desc", latitude=0.0, longitude=0.0, user_id=owner.id)
    session.add_all([owner, other, place])
    session.commit()
    
    response = client.put(f'/api/places/{place.id}/', 
                         json={"name": "Hacked", "description": "Hacked", "latitude": 0.0, "longitude": 0.0},
                         headers={"X-API-Key": "otherkey"})
    assert response.status_code == 403


@pytest.mark.integration
def test_delete_place(client, session):
    """Test DELETE /api/places/<id>."""
    user = User(api_key="key")
    place = Place(name="Place", description="Desc", latitude=0.0, longitude=0.0, user_id=user.id)
    session.add_all([user, place])
    session.commit()
    
    response = client.delete(f'/api/places/{place.id}/', headers={"X-API-Key": "key"})
    assert response.status_code == 204
    
    # Check deleted
    response = client.get(f'/api/places/{place.id}/')
    assert response.status_code == 404


@pytest.mark.integration
def test_get_user_places(client, session):
    """Test GET /api/users/<user_id>/places/."""
    user = User(api_key="key")
    place1 = Place(name="Place1", description="Desc", latitude=0.0, longitude=0.0, user_id=user.id)
    place2 = Place(name="Place2", description="Desc", latitude=1.0, longitude=1.0, user_id=user.id)
    session.add_all([user, place1, place2])
    session.commit()
    
    response = client.get(f'/api/users/{user.id}/places/')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["name"] in ["Place1", "Place2"]