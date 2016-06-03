#!/bin/sh
docker run --name zanatadb \
  -e MYSQL_USER=zanata -e MYSQL_PASSWORD=password -e MYSQL_DATABASE=zanata -e MYSQL_RANDOM_ROOT_PASSWORD=yes \
  -d mysql:5.7 \
  --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

echo 'Please use the command "docker logs zanatadb" to check that MySQL starts correctly.'
