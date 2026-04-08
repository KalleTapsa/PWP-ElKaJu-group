import io

import pytest

from PeculiarPlaces.models import Image, Place, ReportImage, User


@pytest.mark.integration
def test_get_images_empty_place(session, client):
    """Test GET /api/places/<id>/images/ for place with no images."""
    user = User(api_key="test_get_images_empty")
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

    response = client.get(f"/api/places/{place.id}/images/")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.integration
def test_create_image(session, client):
    """Test POST /api/places/<id>/images/ creates an image."""
    user = User(api_key="test_create_image")
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

    file_content = b"Hello World"
    file_data = io.BytesIO(file_content)
    file_data.name = "test.jpg"

    response = client.post(
        f"/api/places/{place.id}/images/",
        content_type="multipart/form-data",
        data={"file": (file_data, "test.jpg")},
        headers={"Authorization": "test_create_image"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Image uploaded successfully"
    assert "id" in data


@pytest.mark.integration
def test_create_image_unauthorized(client):
    """Test POST /api/places/<id>/images/ without auth fails."""

    file_content = b"Hello World"
    file_data = io.BytesIO(file_content)
    file_data.name = "test.jpg"

    response = client.post(
        "/api/places/1/images/",
        content_type="multipart/form-data",
        data={"file": (file_data, "test.jpg")},
    )
    assert response.status_code == 401


@pytest.mark.integration
def test_create_image_no_file(session, client):
    """Test POST /api/places/<id>/images/ without file fails."""
    user = User(api_key="test_create_image_no_file")
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
        f"/api/places/{place.id}/images/",
        data={"description": "No file"},
        headers={"Authorization": "test_create_image_no_file"},
    )
    assert response.status_code == 400


@pytest.mark.integration
def test_create_image_invalid_extension(session, client):
    """Test POST /api/places/<id>/images/ with invalid file type fails."""
    user = User(api_key="test_create_image_invalid_ext")
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

    file_content = b"Hello World"
    file_data = io.BytesIO(file_content)
    file_data.name = "test.txt"

    response = client.post(
        f"/api/places/{place.id}/images/",
        content_type="multipart/form-data",
        data={"file": (file_data, "test.txt")},
        headers={"Authorization": "test_create_image_invalid_ext"},
    )
    assert response.status_code == 400


@pytest.mark.integration
def test_get_image_by_id(session, client):
    """Test GET /api/places/<place_id>/images/<image_id>/."""
    user = User(api_key="test_get_image_by_id")
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

    image = Image(
        image_path="test.jpg", place_id=place.id, user_id=user.id, description="Test"
    )
    session.add(image)
    session.commit()

    response = client.get(f"/api/places/{place.id}/images/{image.id}/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == image.id
    assert data["place_id"] == place.id
    assert data["description"] == "Test"
    assert "image_url" in data


@pytest.mark.integration
def test_get_image_not_found(client):
    """Test GET /api/places/<place_id>/images/<image_id>/ for non-existent image."""
    response = client.get("/api/places/1/images/999/")
    assert response.status_code == 404


@pytest.mark.integration
def test_get_image_wrong_place(session, client):
    """Test GET /api/places/<place_id>/images/<image_id>/ with mismatched place."""
    user = User(api_key="test_get_image_wrong_place")
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

    image = Image(image_path="test.jpg", place_id=place1.id, user_id=user.id)
    session.add(image)
    session.commit()

    response = client.get(f"/api/places/{place2.id}/images/{image.id}/")
    assert response.status_code == 404


@pytest.mark.integration
def test_delete_image(session, client):
    """Test DELETE /api/places/<place_id>/images/<image_id>/."""
    user = User(api_key="test_delete_image")
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

    image = Image(image_path="test.jpg", place_id=place.id, user_id=user.id)
    session.add(image)
    session.commit()

    response = client.delete(
        f"/api/places/{place.id}/images/{image.id}/",
        headers={"Authorization": "test_delete_image"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Image deleted successfully"

    response = client.get(f"/api/places/{place.id}/images/{image.id}/")
    assert response.status_code == 404


@pytest.mark.integration
def test_delete_image_unauthorized(client):
    """Test DELETE /api/places/<place_id>/images/<image_id>/ without auth fails."""
    response = client.delete("/api/places/1/images/1/")
    assert response.status_code == 401


@pytest.mark.integration
def test_delete_image_not_owner(session, client):
    """Test DELETE /api/places/<place_id>/images/<image_id>/ by non-owner fails."""
    owner = User(api_key="test_delete_image_owner")
    session.add(owner)
    session.commit()

    other = User(api_key="test_delete_image_other")
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

    image = Image(image_path="test.jpg", place_id=place.id, user_id=owner.id)
    session.add(image)
    session.commit()

    response = client.delete(
        f"/api/places/{place.id}/images/{image.id}/",
        headers={"Authorization": "test_delete_image_other"},
    )
    assert response.status_code == 403


@pytest.mark.integration
def test_get_user_images(session, client):
    """Test GET /api/users/<user_id>/images/."""
    user = User(api_key="test_get_user_images")
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

    image1 = Image(
        image_path="img1.jpg",
        place_id=place1.id,
        user_id=user.id,
        description="Image 1",
    )
    session.add(image1)
    session.commit()

    image2 = Image(
        image_path="img2.jpg",
        place_id=place2.id,
        user_id=user.id,
        description="Image 2",
    )
    session.add(image2)
    session.commit()

    response = client.get(f"/api/users/{user.id}/images/")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    descriptions = [img["description"] for img in data]
    assert "Image 1" in descriptions
    assert "Image 2" in descriptions


@pytest.mark.integration
def test_get_places_images(session, client):
    """Test GET /api/places/<place_id>/images/ returns all images for place."""
    user = User(api_key="test_get_places_images")
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

    image1 = Image(image_path="img1.jpg", place_id=place.id, user_id=user.id)
    session.add(image1)
    session.commit()

    image2 = Image(image_path="img2.jpg", place_id=place.id, user_id=user.id)
    session.add(image2)
    session.commit()

    response = client.get(f"/api/places/{place.id}/images/")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    image_ids = [img["id"] for img in data]
    assert image1.id in image_ids
    assert image2.id in image_ids
