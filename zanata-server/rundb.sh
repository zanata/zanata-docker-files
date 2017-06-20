#!/bin/bash -eu
### This program sets up the data volume and database containers for Zanata

ScriptFile=$(realpath ${BASH_SOURCE[0]})
ScriptDir=$(dirname $ScriptFile)
source $ScriptDir/common
ensure_docker_network

## Create zanata-db volume if it is missing
if ! (docker volume ls -q | grep zanata-db) ; then
    docker volume create --name zanata-db
fi

if [ -z $(docker ps -aq -f name=zanatadb) ];then
    ## Create new container if zanatadb does not exist
    docker run --name zanatadb \
        -e MYSQL_USER=${ZANATA_MYSQL_USER} -e MYSQL_PASSWORD=${ZANATA_MYSQL_PASSWORD} \
        -e MYSQL_DATABASE=${ZANATA_MYSQL_DATABASE} -e MYSQL_RANDOM_ROOT_PASSWORD=yes \
        -v zanata-db:/var/lib/mysql:Z \
        --net ${ZANATA_DOCKER_NETWORK} \
        -d mariadb:10.1 \
        --character-set-server=utf8 --collation-server=utf8_general_ci
elif [ -n $(docker ps -aq -f name=zanatadb -f status=exited) ];then
    ## Start container if zanatadb stopped
    docker start zanatadb
fi

echo 'Please use the command "docker logs zanatadb" to check that MariaDB starts correctly.'
