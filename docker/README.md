# Docker

Copy `.env.template` as `.env` and adjust content, only required to enable loggin from osm.org.

Build the Docker image, within the docker directory:
```
curl https://osmose.openstreetmap.fr/export/osmose-menu.sql.bz2 | bzcat > osmose-menu.sql
docker-compose build
```

Run the containers:
```
docker-compose up
```

The API server will be running at http://127.0.0.1:20009/
The Web server will be at https://localhost:8080/en/map/


## Docker for development

Run the database int the background:
```
docker-compose up -d postgres
```

### API
```
docker-compose -f docker-compose.yml -f docker-compose-dev.yml -f docker-compose-test.yml run -p 20009:20009 api
```

Once on container, run the standalone API server
```
uvicorn osmose:app --host 0.0.0.0 --port 20009 --reload --reload-delay 2
```

Acces to the database from the API container with
```
psql -h postgres osmose_frontend osmose
```

### Web Server
You can work on Web part easyily without Docker, look at main (README.md)[./README.md]

Using Docker:
```
docker-compose -f docker-compose.yml -f docker-compose-dev.yml run -p 8080:8080 web
```

Once on container, for first time:
```
cd po && make mo && cd ..
npm run dev-server
```

## Data from Osmose Backend
To upload data to Osmose Frontend see the Osmose Backend.

Show the results at: http://localhost:8080/en/issues/open?item=xxxx&useDevItem=all
