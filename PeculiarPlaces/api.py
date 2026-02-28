from flask_restful import Api
from models import app, db
from resources.place import PlaceCollection, PlaceItem, PlacesByUser

api = Api(app, version="1.0", title="PeculiarPlaces API")

api.add_resource(PlaceCollection, "/api/places/")
api.add_resource(PlaceItem, "/api/places/<place:place>/")
api.add_resource(PlacesByUser, "/api/users/<int:user_id>/places/")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)