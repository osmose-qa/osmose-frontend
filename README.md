# Frontend part of Osmose-QA tool

This is the part of [Osmose-QA](http://osmose.openstreetmap.fr) that shows issues on a map.

## Translation

Interested in helping translate Osmose? Contribute on [Transifex](https://explore.transifex.com/openstreetmap-france/osmose/).

## Contribution

### Web

The HTML/JS part is in Vue.js. You can run de development instance locally using the public Osmose-QA Frontend API. The `dev-server` and `dev-server-public` have browser hot code reload. `dev-server` need a local API server, while `dev-server-public` use the API of `osmose.openstreetmap.fr`.

```
cd web
npm install
npm run dev-server-public
```

Then go to http://localhost:8081/

Chack your code with ESLint
```
npm run lint
```

### API Server

To run Osmose Frontend API Server, preferably use Docker. Follow the documentation in the [docker](docker/README.md) directory. You can also install the Frontend manually by following the [install guide](INSTALL.md).

The API documentation is available on [/api/docs](https://osmose.openstreetmap.fr/api/docs).
