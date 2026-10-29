# Client side HTML/JS

The HTML/JS part is in Vue.js. You can run de development instance locally using the public Osmose-QA Frontend API.

## Dev using Docker

From the root dir.

Copy `.env.template` as `.env` adjust:
- uncomment the `COMPOSE_FILE=docker-compose.yml:docker-compose-dev.yml` line,
- by default it will connect to local API, if you wan to only dev on the web part, comment the `API_URL=http://localhost:20009` and use the public API at https://osmose.openstreetmap.fr

Then run the service.

```
docker compose watch web
```

Once up, you can edit file it will do hot rebuild et reload.

The Web server will be at http://localhost:8080/en/map/

Check your code with ESLint
```
npm run lint
```
