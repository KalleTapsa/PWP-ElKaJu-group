from PeculiarPlaces.models import User


def create_authenticated_client(
    client, session, username="testuser", api_key="testkey"
):
    """Create a test client with an authenticated user."""
    user = User(api_key=api_key)
    session.add(user)
    session.commit()
    client.api_key = api_key  # Store for convenience
    return client


def authenticated_request(client, method, url, api_key=None, **kwargs):
    """Make a request with API key header."""
    if api_key is None:
        api_key = getattr(client, "api_key", None)
    if api_key:
        headers = kwargs.get("headers", {})
        headers["Authorization"] = api_key
        kwargs["headers"] = headers
    return getattr(client, method.lower())(url, **kwargs)
