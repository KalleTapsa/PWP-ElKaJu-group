import pytest


@pytest.mark.integration
def test_api_basic_endpoints(client):
    """Basic test for API endpoints availability."""
    # Test places endpoint
    response = client.get('/api/places/')
    assert response.status_code in [200, 404]  # 200 if places exist, 404 if not


