#!/bin/bash -eu
### This program setups the data volume and database containers for Zanata

: ${ZANATA_MYSQL_USER:=zanata}
: ${ZANATA_MYSQL_PASSWORD:=password}
: ${ZANATA_MYSQL_DATABASE:=zanata}

## Create missing data volume
if ! (docker volume ls -q | grep zanata-data) ; then
    docker volume create --name zanata-data
fi

## Run container when no container named zanatadb
if [ -z $(docker ps -aq -f name=zanatadb) ];then
    docker run --name zanatadb \
	-e MYSQL_USER=${ZANATA_MYSQL_USER} -e MYSQL_PASSWORD=${ZANATA_MYSQL_PASSWORD} \
	-e MYSQL_DATABASE=${ZANATA_MYSQL_DATABASE} -e MYSQL_RANDOM_ROOT_PASSWORD=yes \
	-v zanata-data:/opt/jboss \
        -d mariadb:10.1 \
	--character-set-server=utf8 --collation-server=utf8_general_ci
elif [ -n $(docker ps -aq -f name=zanatadb -f status=exited) ];then
    docker start zanatadb
fi

echo 'Please use the command "docker logs zanatadb" to check that MariaDB starts correctly.'
