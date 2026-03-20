from .models import User

def fetch_api_key(api_key_str):
    """
    Validates the key and returns it if valid, otherwise returns None.
    """
    user = User.query.filter_by(api_key=api_key_str).first()
    if user:
        return api_key_str
    return None