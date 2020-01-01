#!/bin/bash

set -e

# TODO: Consider deleting your old assets if you're md5 tagging them.
#rm -rf /app/public/css /app/public/js /app/public/fonts /app/public/images

cp -a /public /app

exec "$@"
