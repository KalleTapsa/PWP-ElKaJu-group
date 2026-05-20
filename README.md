# PWP SPRING 2026
# Peculiar Places
# Group information
* Jussi Saariniemi jsaarini20@student.oulu.fi
* Kalle Tapio ktapio21@student.oulu.fi
* Elisa Tscholakov etschola25@student.oulu.fi

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint, instructions on how to setup and run the client, instructions on how to setup and run the axiliary service and instructions on how to deploy the api in a production environment__

# API Overview
Our project is a Flask-based web API using Flask-SQLAlchemy as the ORM.
The database stores users, places, images, reviews and reports for places, images and reviews.


__Project Dependencies__
* Python Version 3.12+
* Flask 
* Flask-SQLAcademy
* SQLite (default database)

# DELIVERY 2 DATABASE
__Database Setup:__
[models.py](https://github.com/user-attachments/files/25162038/models.py)


__Population Script:__
[setup_and_populate.py](https://github.com/user-attachments/files/25161808/setup_and_populate.py)

# DELIVERY 3

# HOW TO RUN (WINDOWS):
1. *Navigate to PWP-ElKaJu-group folder*
2. python -m venv venv
3. venv\Scripts\activate
4. pip install -e .
5. flask --app PeculiarPlaces init-db
6. flask --app PeculiarPlaces run --debug
7. *The API can be found in http://127.0.0.1:5000/api/*

# HOW TO RUN TESTS (WINDOWS):
1. *Navigate to PWP-ElKaJu-group folder*
2. python -m venv venv
3. venv\Scripts\activate
4. pip install -e .
5. pytest

# DEPENDENCIES:
"flask==2.3.3",
"flask-restful",
"flask-sqlalchemy",
"flask-caching",
"flask-api-key",
"flasgger",
"pytest",
"pytest-flask",
"factory-boy",
"pytest-cov"

DOCUMENTATION IN http://127.0.0.1:5000/apidocs/

# DELIVERY 4
1. *Navigate to client folder*
2. npm install
3. npm run dev
4. *if api is running client will work properly*
