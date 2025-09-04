Manual Installation
-------------------

This guide is compatible with Ubuntu 18.04 and Ubuntu 20.04

### Dependencies

```
apt install python3 python3-dev virtualenv gcc pkg-config libpng-dev libjpeg-dev libfreetype6-dev postgresql-server-dev-all libgeos-dev g++ python3-shapely nodejs npm
```

#### Database

```
apt install postgresql postgresql-contrib postgresql-postgis
```

#### Web server

```
apt install apache2 libapache2-mod-wsgi-py3
```

#### Internationalisation and SVG rendering

```
apt install gettext librsvg2-bin
```

### Initialisation

Generate translation files
```
(cd web/po && make mo)
```


### Python

Osmose QA frontend requires python >= 3

Create a python virtualenv, active it and install python dependencies
```
virtualenv --python=python3 osmose-frontend-venv
source osmose-frontend-venv/bin/activate
pip install -r requirements.txt -r requirements-prod.txt
```

To run osmose as systemd service runned by the gunicorn webserver, use this as `/etc/systemd/system/gunicorn.service`.

```
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
PIDFile = /run/gunicorn-osmose/osmose.pid
User=osmose
Group=osmose
RuntimeDirectory=gunicorn-osmose
WorkingDirectory=/data/project/osmose/frontend/
Environment=PYTHONPATH=/data/project/osmose/frontend/osmose-frontend-venv/lib/python3.9/site-packages/
ExecStart=/data/project/osmose/frontend/osmose-frontend-venv/bin/gunicorn osmose:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --pid /run/gunicorn-osmose/osmose.pid
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Run and get logs using:
```
systemctl daemon-reload
systemctl enable gunicorn
systemctl start gunicorn
journalctl -u gunicorn
```

### Database

Start the postgrsql server, then as the `postgres` user:
```
createuser -s osmose
# Set your own password
psql -c "ALTER ROLE osmose WITH PASSWORD '-osmose-';"
createdb -E UTF8 -T template0 --lc-collate=fr_FR.UTF-8 --lc-ctype=fr_FR.UTF-8 -O osmose osmose_frontend
# Enable extensions
psql -c "CREATE EXTENSION pgcrypto" osmose_frontend
```

Go back to your original user and create the database tables.
```
psql --user osmose osmose_frontend -f tools/database/schema.sql
```

Check data base parameter into `modules/utils.py`.


### Generate markers
```
(cd tools && ./make-markers.py)
```


### Web assets

To package web assets, including previously generated markers, run
```
(cd web     && npm install && npm run build)
(cd web_api && npm install && npm run build)
```


### Web Server

As root user, copy `apache-site` to `/etc/apache2/sites-available/osmose.conf`:
```
cp apache-site /etc/apache2/sites-available/osmose.conf
```

Adjust the config, if needed. Especially the user and group running the process in
`WSGIDaemonProcess` and `WSGIProcessGroup`, and path in `WSGIScriptAlias`,
`DocumentRoot`, `Alias`s and `Directory`.

If you setup a python virtualenv add the appropriate `python-path=/home/osmose/osmose-frontend-venv/lib/python3.8/site-packages`
at the and of WSGIDaemonProcess line.

Enable the new config:
```
a2dissite 000-default.conf
a2ensite osmose.conf
a2enmod rewrite.load wsgi.load expires.load cache_disk.load cache.load
service apache2 reload
```

Change the server URL into `website` in file `modules/utils.py`.


### Database translations

When some issues are in the database, to get translations use (still in virtualenv):
```
(cd tools && ./menu_update.py)
```

### Daily tasks

Adjust DIR_DUMP at the start of `tools/cron.sh` then set this script to execute once a day (with `crontab` for example)
Depending on your database configuration, you may need to pass additional environment variables (see `man 1 psql`):
```
tools/cron.sh
```
