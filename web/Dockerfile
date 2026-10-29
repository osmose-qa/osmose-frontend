FROM node:26-alpine3.23
ENV LANG en_US.UTF-8
ENV API_URL https://osmose.openstreetmap.fr

RUN apk add --no-cache --update \
        gettext \
        make

WORKDIR /data/project/osmose/frontend/web

ADD package.json package-lock.json webpack.config.js .
RUN npm install

ADD . ./
RUN npm run build

CMD npm run server
EXPOSE 8080
