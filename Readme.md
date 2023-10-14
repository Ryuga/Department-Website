# Website for the Department of Computer Science
## Christ College (Autonomous) Irinjalakuda

## Setup instruction


#### You would need a linux system for development. Windows raises python-decouple errors. More info [here](https://github.com/ryuga/Department-Website/issues/1).
#### You need Python 3.8 or above installed on your system.


### Development Setup
```bash
# Clone the repository or download as zip and cd into the root folder (Department-Website)
# Terminal instructions (You're supposed run the below commands during the initial setup)

# Remove existing virtualenv module, We will let poetry install the required version
$ sudo apt-get remove virtualenv -y && sudo python3 -m pip uninstall virtualenv -y

# Install poetry
$ pip install poetry

# Install dependencies from poetry
$ poetry install

$ sudo nano .env
# add the following environment variables

DATABASE_URL = your_database_url

DEBUG = True
LOCAL_DEVELOPMENT = True
SECRET_KEY = "your_secret_key"
DASHBOARD_URL = "your_dashboard_url"
ENCRYPTION_SALT = "your_encryption_salt"
ENCRYPTION_ITERATION = your_iteration_count


PAYTM_MERCHANT_ID = "your_merchant_id"
PAYTM_MERCHANT_KEY = "your_merchant_key"

GOOGLE_CLIENT_ID = "your_client_id"
GOOGLE_CLIENT_SECRET = "your_client_secret"

# Run the development server locally
$ poetry run python3 manage.py runserver 
# this should run the Django development server on your localhost:8000.
# now you can visit http://127.0.0.1:8000 and access the site.
```

### Adding host file configuration for subdomain access in development

### Production Setup

#### Addition Requirements:

[NGINX](https://nginx.org/en/): Webserver for handling requests and serving django assets.

[Supervisor](http://supervisord.org/): Process management tool for keeping Django running. It also provides logging in events of unaccounted crashes and restarts the application to keep it online.


#### Setup procedure for Ubuntu 20.04 LTS. This will also work for all Debian/Ubuntu based distros. Procedures for other distros maybe slightly different but follows almost the same flow.
```bash
# Clone the repository or download as zip and cd into the root folder (Department-Website)

# Update and upgrade apt
$ sudo apt update && sudo apt upgrade -y

# If pip is not installed
$ sudo apt-get install python3-pip -y

# Remove virtualenv and let poetry install the required version
$ sudo apt-get remove virtualenv -y && sudo python3 -m pip uninstall virtualenv -y

# Clone the repository and cd into the folder
$ git clone https://github.com/Ryuga/Department-Website.git && cd Department-Website

# Install poetry
$ sudo python3 -m pip install poetry

# Install dependencies from poetry
$ sudo poetry install

$ sudo nano .env
# add the following environment variables

DATABASE_URL = your_database_url

DEBUG = False
LOCAL_DEVELOPMENT = False
SECRET_KEY = "your_secret_key"
DASHBOARD_URL = "your_dashboard_url"
ENCRYPTION_SALT = "your_encryption_salt"
ENCRYPTION_ITERATION = your_encryption_iteration_count

PAYTM_MERCHANT_ID = "your_merchant_id"
PAYTM_MERCHANT_KEY = "your_merchant_key"

GOOGLE_CLIENT_ID = "your_client_id"
GOOGLE_CLIENT_SECRET = "your_client_secret"

# Run collectstatic to collect static files to assets folder for production
$ sudo poetry run python3 manage.py collectstatic

# install supervisord
$ sudo apt install supervisor -y

# install nginx
$ sudo apt install nginx -y
```
At this point, nginx should be running. 

If inbound connections are enabled for port 80, you'll be able to visit the ip with a browser which should give you the default NGINX landing page.

#### Supervisord configurations
add the below config inside `/etc/supervisor/conf.d/gunicorn.conf`
```shell
[program:gunicorn]
directory=/home/ubuntu/Department-Website
command=poetry run python3 -m gunicorn --workers 3 --bind unix:/home/ubuntu/Department-Website/app.sock core.wsgi:application
autostart=true
autorestart=true
stderr_logfile=/var/log/gunicorn/gunicorn.err.log
stdout_logfile=/var/log/gunicorn/gunicorn.out.log

[group:guni]
programs:gunicorn
```

Make log and output files for supervisor
```bash
$ sudo mkdir /var/log/gunicorn && cd /var/log/gunicorn

$ sudo touch gunicorn.out.log
$ sudo touch gunicorn.err.log
```
Update supervisor to propagate changes

```bash
# Reread supervisor configurations
$ sudo supervisorctl reread

# Update supervisor configurations
$ sudo supervisorctl update

# Check if supervisor is correctly configured. 
$ sudo supervisorctl status
# If correctly configured the application should be running with pid and shows uptime. 
# Otherwise check the configurations or logs and try again.

# In case if supervisor status shows restarting, 
# 1) Check if gunicorn is installed 
# 2) check if the log and output files exist for supervisor
# 3) check the logs and check the Django application

# In case if supervisor status shows exited quickly
# 1) check if the directory and commands in the gunicorn.conf is correct
# 2) check the application, the environment variables, database.
```

#### NGINX Configurations

add the below config inside `/etc/nginx/sites-available/django.conf`

```shell
server {
        listen 80;
#        listen 443 ssl http2;
#        listen [::]:443 ssl http2;
#        ssl on;
#        ssl_certificate         /etc/ssl/certs/cert.pem;
#        ssl_certificate_key     /etc/ssl/private/key.pem;
#        ssl_client_certificate /etc/ssl/certs/cloudflare.crt;
#        ssl_verify_client on;

        server_name <ip_address_or_domain_here>;

        location / {
                include proxy_params;
                proxy_pass http://unix:/home/ubuntu/Department-Website/app.sock;
        }
        location /static/ {
                autoindex on;
                alias /home/ubuntu/Department-Website/assets/;
        }   
        location /protected/media/ {
                internal;
                alias /home/ubuntu/Department-Website/media/;
        }
    
}
```
Once added, test if the configurations are okay and symlink with `sites-enabled`

```bash
$ sudo nginx -t
# If configurations are not okay, Check the nginx configuration again to see if paths added are correct

# If configurations shows okay, Symlink with sites-enabled
$ sudo ln  /etc/nginx/sites-available/django.conf /etc/nginx/sites-enabled

# Test nginx again
$ sudo nginx -t

# If configuration shows okay, Reload nginx
$ sudo systemctl reload nginx

# Reload supervisor
$ sudo systemctl reload supervisor
```

#### Once all the above setups are complete, we'll be able to visit the site in the domain/ip provided in the nginx configuration.
