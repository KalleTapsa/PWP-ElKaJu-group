import requests

BASE_URL = "http://127.0.0.1:5000/api"

# Test get all places
response = requests.get(f"{BASE_URL}/places/")
print("All places:", response.json())

# Test create place
place_data = {
    "name": "Test Place",
    "latitude": 60.1699,
    "longitude": 24.9384
}
response = requests.post(f"{BASE_URL}/places/", json=place_data)
print("Created place:", response.json())

# Test get review
response = requests.get(f"{BASE_URL}/reviews/1/")
print("Review:", response.json())
