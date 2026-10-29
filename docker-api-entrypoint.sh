#!/bin/bash

set -eu

if [ ! -f api/assets/marker-gl-sprite.json ]; then
    echo "Generating sprites"
    cd tools && python ./make-markers.py && cd -
fi

exec "$@"
