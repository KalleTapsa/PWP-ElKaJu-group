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

# HOW TO RUN
1. *Navigate to client folder*
2. npm install
3. npm run dev
4. *if api is running client will work properly*

# DEPLOYING API AND CLIENT
1. *ssh to your server*
2. sudo apt update
3. sudo apt install python3.12-venv python3-pip supervisor nginx nodejs npm git -y
4. sudo groupdel peculiarplaces 2>/dev/null
5. sudo useradd --system peculiarplaces
6. sudo mkdir /home/peculiarplaces
7. sudo chown peculiarplaces:peculiarplaces /home/peculiarplaces
8. sudo mkdir /opt/peculiarplaces
9. sudo chown peculiarplaces:peculiarplaces /opt/peculiarplaces
10. sudo chmod -R o-rwx /opt/peculiarplaces
11. sudo -u peculiarplaces git clone https://github.com/KalleTapsa/PWP-ElKaJu-group.git /opt/peculiarplaces/app
12. sudo -u peculiarplaces python3 -m venv /opt/peculiarplaces/venv
13. sudo -u peculiarplaces /opt/peculiarplaces/venv/bin/pip install gunicorn
14. sudo -u peculiarplaces /opt/peculiarplaces/venv/bin/pip install -e /opt/peculiarplaces/app
15. sudo -u peculiarplaces bash -c "cd /opt/peculiarplaces/app && /opt/peculiarplaces/venv/bin/flask --app=PeculiarPlaces init-db"
16. sudo -u peculiarplaces mkdir /opt/peculiarplaces/venv/scripts
17. sudo -u peculiarplaces tee /opt/peculiarplaces/venv/scripts/start_gunicorn > /dev/null << 'EOF'
#!/bin/sh
cd /opt/peculiarplaces/app
exec /opt/peculiarplaces/venv/bin/gunicorn -w 3 -b 127.0.0.1:5000 "PeculiarPlaces:create_app()"
EOF
18. sudo chmod u+x /opt/peculiarplaces/venv/scripts/start_gunicorn
19. sudo -u peculiarplaces mkdir /opt/peculiarplaces/logs
20. sudo tee /etc/supervisor/conf.d/peculiarplaces.conf > /dev/null << 'EOF'
[program:peculiarplaces]
command = /opt/peculiarplaces/venv/scripts/start_gunicorn
autostart = true
autorestart = true
user = peculiarplaces
stdout_logfile = /opt/peculiarplaces/logs/gunicorn.log
redirect_stderr = true
EOF
21. sudo systemctl reload supervisor
22. sudo -u peculiarplaces bash -c "cd /opt/peculiarplaces/app/CoolRocks/client && npm install && npm run build"
23. sudo mkdir -p /var/www/peculiarplaces
24. sudo cp -r /opt/peculiarplaces/app/CoolRocks/client/dist/. /var/www/peculiarplaces/
25. sudo chown -R www-data:www-data /var/www/peculiarplaces
26. sudo tee /etc/nginx/sites-available/peculiarplaces > /dev/null << 'EOF'
server {
    listen 80;
    server_name <your-server-ip-or-hostname>;

    root /var/www/peculiarplaces;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $http_host;
    }

    location /apidocs/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $http_host;
    }

    location /flasgger_static/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $http_host;
    }

    location /apispec_1.json {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $http_host;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF
27. sudo ln -s /etc/nginx/sites-available/peculiarplaces /etc/nginx/sites-enabled/
28. sudo rm -f /etc/nginx/sites-enabled/default
29. sudo nginx -t && sudo systemctl reload nginx
