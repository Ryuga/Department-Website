# Website for the Department of Computer Science
## Christ College (Autonomous) Irinjalakuda

## Setup instruction

#### You need Python 3.8 or above installed on your system.


### Development Setup
```bash
# Clone the repository or download as zip and cd into the root folder (Department-Website)
# Terminal instructions (You're supposed run the below commands during the initial setup)

# Install pipenv 
$ pip install pipenv

# Install dependencies from Pipenv
$ pipenv install

$ touch .env
# setup the following environment variables

SECRET_KEY = "your_secret_key"
DB_NAME = "your_db_name"
DB_HOST = "your_db_host"
DB_PASS = "your_db_password"
DB_USER = "your_db_user"
DEBUG = True

# Run the development server locally
$ pipenv run server
# this should run the Django development server on your localhost:8000.
# now you can visit http://127.0.0.1:8000 and access the site.
```


### Production Setup

#### Addition Requirements:

[NGINX](https://nginx.org/en/): Webserver for handling requests and serving django assets.

[Supervisor](http://supervisord.org/): Process management tool for keeping Django running. It also provides logging in events of unaccounted crashes and restarts the application to keep it online.


#### Setup procedure for Ubuntu 20.04 LTS. This will also work for all Debian/Ubuntu based distros. Procedures for other distros maybe slightly different but follows almost the same flow.
```bash
# Clone the repository or download as zip and cd into the root folder (Department-Website)

# Update and upgrade apt
$ sudo apt update && sudo apt upgrade -y

# Install pipenv (any one method)
$ pip3 install pipenv | python3 -m pip install pipenv | sudo apt install pipenv -y

# Install dependencies from Pipenv
$ sudo pipenv install

$ touch .env
# setup the following environment variables

SECRET_KEY = "your_secret_key"
DB_NAME = "your_db_name"
DB_HOST = "your_db_host"
DB_PASS = "your_db_password"
DB_USER = "your_db_user"
DEBUG = True

# Run collectstatic to collect static files to assets folder for production
$ sudo pipenv run python manage.py collectstatic

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
command=pipenv run gunicorn --workers 3 --bind unix:/home/ubuntu/Department-Website/app.sock core.wsgi:application
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

add the below config inside `/etc/nginx/site-available/django.conf`

```shell
server {
        listen 80;
        #listen 443 ssl http2;
        #listen [::]:443 ssl http2;
        #ssl on;
        #ssl_certificate         /etc/ssl/certs/cert.pem;
        #ssl_certificate_key     /etc/ssl/private/key.pem;
        #ssl_client_certificate /etc/ssl/certs/cloudflare.crt;
        #ssl_verify_client on;

        server_name <ip_address_or_domain_here>;

        location / {
                include proxy_params;
                proxy_pass http://unix:/home/ubuntu/Department-Website/app.sock;
                }
        location /static/ {
                autoindex on;
                alias /home/ubuntu/Department-Website/assets/;
    }   
}
```
Once added, test if the configurations are okay and symlink with `sites-enabled`

```bash
$ sudo nginx -t
# If configurations are not okay, Check the nginx configuration again to see if paths added are correct

# If configurations shows okay, Symlink with sites-enabled
$ sudo ln  /etc/nginx/site-available/django.conf /etc/nginx/sites-enabled

# Test nginx again
$ sudo nginx -t

# If configuration shows okay, Reload nginx
$ sudo systemctl reload nginx

# Reload supervisor
$ sudo systemctl reload supervisor
```

#### Once all the above setups are complete, we'll be able to visit the site in the domain/ip provided in the nginx configuration.
