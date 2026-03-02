import requests

BASE_URL = "http://127.0.0.1:5000/api"

# Test get all places
response = requests.get(f"{BASE_URL}/places/")
print("All places:", response.json())

# Test get review
response = requests.get(f"{BASE_URL}/reviews/1/")
print("Review:", response.json())


response = requests.get(f"{BASE_URL}/reviews/10/")
print("Review:", response.json())