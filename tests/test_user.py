import pytest

from PeculiarPlaces.models import User


@pytest.mark.integration
def test_create_user(session, client):
    """Test POST /api/users/ creates a new user."""
    response = client.post("/api/users/")
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert "api_key" in data
    assert data["message"] == "Save the API key. It will not be shown again."
    assert len(data["api_key"]) == 64


@pytest.mark.integration
def test_create_user_saves_to_db(session, client):
    """Test POST /api/users/ saves user to database."""
    response = client.post("/api/users/")
    assert response.status_code == 201
    data = response.get_json()

    user = User.query.get(data["id"])
    assert user is not None
    assert user.api_key == data["api_key"]


@pytest.mark.integration
def test_create_user_unique_api_key(session, client):
    """Test POST /api/users/ generates unique API key for each user."""
    response1 = client.post("/api/users/")
    data1 = response1.get_json()

    response2 = client.post("/api/users/")
    data2 = response2.get_json()

    assert data1["api_key"] != data2["api_key"]
    assert data1["id"] != data2["id"]


@pytest.mark.integration
def test_delete_user(session, client):
    """Test DELETE /api/users/<id>/ deletes user successfully."""
    user = User(api_key="test_delete_user")
    session.add(user)
    session.commit()

    response = client.delete(
        f"/api/users/{user.id}/", headers={"Authorization": "test_delete_user"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "User and all associated data deleted successfully"


@pytest.mark.integration
def test_delete_user_unauthorized(client):
    """Test DELETE /api/users/<id>/ without auth fails."""
    response = client.delete("/api/users/1/")
    assert response.status_code == 401


@pytest.mark.integration
def test_delete_user_not_found(session, client):
    """Test DELETE /api/users/<id>/ for non-existent user."""
    user = User(api_key="test_delete_user_not_found")
    session.add(user)
    session.commit()

    response = client.delete(
        "/api/users/999/", headers={"Authorization": "test_delete_user_not_found"}
    )
    assert response.status_code == 403


@pytest.mark.integration
def test_delete_user_not_owner(session, client):
    """Test DELETE /api/users/<id>/ by another user fails."""
    user1 = User(api_key="test_delete_user_not_owner_1")
    session.add(user1)
    session.commit()

    user2 = User(api_key="test_delete_user_not_owner_2")
    session.add(user2)
    session.commit()

    response = client.delete(
        f"/api/users/{user1.id}/",
        headers={"Authorization": "test_delete_user_not_owner_2"},
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["error"] == "You can only delete your own user"
