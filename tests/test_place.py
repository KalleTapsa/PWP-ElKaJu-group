import pytest

from PeculiarPlaces.models import Place, User


@pytest.mark.integration
def test_get_places_empty(session, client):
    """Test GET /api/places/."""
    response = client.get("/api/places/")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


@pytest.mark.integration
def test_create_place(session, client):
    """Test POST /api/places/ creates a place."""
    user = User(api_key="test_create_place")
    session.add(user)
    session.commit()

    response = client.post(
        "/api/places/",
        json={
            "name": "Test Place",
            "description": "A test place",
            "latitude": 10.0,
            "longitude": 20.0,
        },
        headers={"Authorization": "test_create_place"},
    )
    assert response.status_code == 201
    data = response.get_json()
    print("aaaa", data)
    assert data["message"] == "Place created successfully"
    assert "id" in data
    assert "Location" in response.headers


@pytest.mark.integration
def test_create_place_unauthorized(client):
    """Test POST /api/places/ without auth fails."""
    response = client.post(
        "/api/places/",
        json={
            "name": "Test Place",
            "description": "A test place",
            "latitude": 10.0,
            "longitude": 20.0,
        },
    )
    assert response.status_code == 401


@pytest.mark.integration
def test_get_place_by_id(session, client):
    """Test GET /api/places/<id>."""
    user = User(api_key="test_get_place_by_id")
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

    response = client.get(f"/api/places/")
    assert response.status_code == 200
    data = response.get_json()
    assert data != []


@pytest.mark.integration
def test_get_place_not_found(session, client):
    """Test GET /api/places/<id> for non-existent place."""
    response = client.get("/api/places/999/")
    assert response.status_code == 404


@pytest.mark.integration
def test_update_place(session, client):
    """Test PUT /api/places/<id>."""
    user = User(api_key="test_update_place")
    session.add(user)
    session.commit()
    place = Place(
        name="Old Name",
        description="Desc",
        latitude=0.0,
        longitude=0.0,
        user_id=user.id,
    )
    session.add(place)
    session.commit()

    response = client.put(
        f"/api/places/{place.id}/",
        json={
            "name": "New Name",
            "description": "Updated",
            "latitude": 1.0,
            "longitude": 1.0,
        },
        headers={"Authorization": "test_update_place"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Place updated successfully"


@pytest.mark.integration
def test_update_place_not_owner(client, session):
    """Test PUT /api/places/<id> by non-owner fails."""
    owner = User(api_key="test_update_place_not_owner")
    other = User(api_key="test_update_place_not_owner2")
    place = Place(
        name="Place", description="Desc", latitude=0.0, longitude=0.0, user_id=owner.id
    )
    session.add_all([owner, other, place])
    session.commit()

    response = client.put(
        f"/api/places/{place.id}/",
        json={
            "name": "Hacked",
            "description": "Hacked",
            "latitude": 0.0,
            "longitude": 0.0,
        },
        headers={"Authorization": "test_update_place_not_owner2"},
    )
    assert response.status_code == 403


@pytest.mark.integration
def test_delete_place(client, session):
    """Test DELETE /api/places/<id>."""
    user = User(api_key="test_delete_place")
    session.add(user)
    session.commit()
    place = Place(
        name="Place", description="Desc", latitude=0.0, longitude=0.0, user_id=user.id
    )
    session.add(place)
    session.commit()

    response = client.delete(
        f"/api/places/{place.id}/", headers={"Authorization": "test_delete_place"}
    )
    assert response.status_code == 204

    # Check deleted
    response = client.get(f"/api/places/{place.id}/")
    assert response.status_code == 404


@pytest.mark.integration
def test_get_user_places(client, session):
    """Test GET /api/users/<user_id>/places/."""
    user = User(api_key="test_get_user_places")
    session.add(user)
    session.commit()
    place1 = Place(
        name="Place1", description="Desc", latitude=0.0, longitude=0.0, user_id=user.id
    )
    place2 = Place(
        name="Place2", description="Desc", latitude=1.0, longitude=1.0, user_id=user.id
    )
    session.add_all([place1, place2])
    session.commit()

    response = client.get(f"/api/users/{user.id}/places/")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["name"] in ["Place1", "Place2"]
