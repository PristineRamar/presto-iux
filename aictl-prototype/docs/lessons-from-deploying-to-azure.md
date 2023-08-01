# Azure Deployment Lessons

- `gunicorn` doesn't load environmental variables from `.env` by default. We need to add the following piece of code to load them manually.

```python
# app_config.py
from dotenv import load_dotenv

load_dotenv(f'{os.environ["HOME"]}/aictl-prototype/aictl/.env')
```

- Specify explicitly the path to static files

```python
# app.py
 app = Flask(__name__, static_url_path="/static/")
```

- Set REDIRECT url to point to DOMAIN name instead of localhost/127.0.0.1

```python
DOMAIN_REDIRECT_URL = "https://aictl.centralindia.cloudapp.azure.com/getAToken"
IS_RUNNING_GUNICORN = None

...

redirect_uri = url_for("auth_response", _external=True)
if IS_RUNNING_GUNICORN:
    redirect_uri = DOMAIN_REDIRECT_URL
```

- Create a service that runs the flask app with gunicorn

```conf
[Unit]
Description=Gunicorn instance for a AICTL flask app
After=network.target
[Service]
User=suriya
Group=www-data
WorkingDirectory=/home/suriya/aictl-prototype/aictl/
ExecStart=/home/suriya/.local/bin/gunicorn -b localhost:5001 app:app
Restart=always
[Install]
WantedBy=multi-user.target
```

Start/Reload aictl service.

```bash
sudo systemctl daemon-reload
sudo systemctl start aictl  # restart/stop
```

- Setup nginx reverse proxy server

```bash
sudo apt install nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

- Get SSL certificates from CertBot

```bash
$ sudo snap install core; sudo snap refresh core
$ sudo snap install --classic certbot
$ sudo ln -s /snap/bin/certbot /usr/bin/certbot
$ sudo certbot --nginx
```

- Configure nginx

````conf

```conf
user www-data;
worker_processes auto;
pid /run/nginx.pid;
error_log  /var/log/nginx/error.log;
include /etc/nginx/modules-enabled/*.conf;

events {
        worker_connections 4096;
        # multi_accept on;
}

http {
  server {
            listen 80;
            listen 443 default ssl;
            server_name aictl.centralindia.cloudapp.azure.com;

	    ssl_certificate /etc/letsencrypt/live/aictl.centralindia.cloudapp.azure.com/fullchain.pem; # managed by Certbot
	    ssl_certificate_key /etc/letsencrypt/live/aictl.centralindia.cloudapp.azure.com/privkey.pem; # managed by Certbot

            access_log /var/log/nginx/access.log;

            location / {
              proxy_pass http://127.0.0.1:5001;
              error_log /var/log/flask-errors.log;
            }
      }
}
````
