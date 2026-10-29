#!/bin/bash
set -eu

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER osmose;
    ALTER ROLE osmose WITH PASSWORD 'clostAdtoi';
    CREATE DATABASE osmose_frontend OWNER osmose TEMPLATE template0;
    GRANT ALL PRIVILEGES ON DATABASE osmose_frontend TO osmose;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "osmose_frontend" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS pgcrypto;
    CREATE EXTENSION IF NOT EXISTS postgis;
EOSQL

psql -v ON_ERROR_STOP=1 --username "osmose" --dbname "osmose_frontend" < /schema.sql

if [[ -n "$LOAD_MENU" ]]; then
    wget -O - https://osmose.openstreetmap.fr/export/osmose-menu.sql.bz2 | bzip2 -d > /tmp/osmose-menu.sql
    psql -v ON_ERROR_STOP=1 --username "osmose" --dbname "osmose_frontend" < /tmp/osmose-menu.sql
fi
