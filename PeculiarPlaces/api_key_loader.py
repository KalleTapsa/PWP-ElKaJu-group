from .models import User

def fetch_api_key(api_key_str):
    """
    Validates the key and returns it if valid, otherwise returns None.
    """
    user = User.query.filter_by(api_key=api_key_str).first()
    return user