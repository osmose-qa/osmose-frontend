# Frontend part of Osmose-QA tool

This is the part of [Osmose-QA](http://osmose.openstreetmap.fr) that shows issues on a map. It includes a database of issues, an API and a web part.

Tha part that check the OpenStreetMap data is on the [Osmose Backend](https://github.com/osmose-qa/osmose-backend/) project.

## Translation

Interested in helping translate Osmose? Contribute on [Weblate](https://hosted.weblate.org/engage/osmose/).

## Code Contribution

To run Osmose Frontend API Server, preferably use Docker. You can also install the Frontend manually by following the [install guide](INSTALL.md).

The API documentation is available on [/api/docs](https://osmose.openstreetmap.fr/api/docs). Docuement also available on the [OSM Wiki](https://wiki.openstreetmap.org/wiki/Osmose).

## Contribution to Web Only

See [web/README.md](web).

## Contribution to Database, API and Web

### Setup

Copy `.env.template` as `.env` and uncomment the `COMPOSE_FILE` line.

Build the Docker images
```bash
docker compose build
```

Init database and generate the marker sprites from menu items.
```
curl -L https://osmose.openstreetmap.fr/export/osmose-menu.sql.bz2 | bzcat > osmose-menu.sql
docker compose run --rm api bash -c "cd tools && python ./make-markers.py"
```

### Run

Then run the services.
```bash
docker compose up
```

The API server will be running at http://127.0.0.1:20009/
The Web server will be at http://localhost:8080/en/map/#item=xxxx&useDevItem=all

### Dev

Python and TypeScript are with hot reload.

If required, acces the database with
```bash
docker compose exec -u postgres postgres psql
```

To upload data to Osmose Frontend see the Osmose Backend.

Show the results at: http://localhost:8080/en/issues/open?item=xxxx&useDevItem=all

### Maintenance

Update .pot translation file with
```
echo "cd po && make" | docker compose run --rm --entrypoint /bin/sh web
```
