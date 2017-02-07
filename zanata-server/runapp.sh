#!/bin/bash -eu
ScriptDir=$(dirname $(realpath $0))

if [ -n "${ZANATA_VERSION-}" ];then
    ## Use the version from set environment ZANATA_VERSION
    ZanataVer=$ZANATA_VERSION
else
    ## Use the latest version (not necessarily the version defined in the Dockerfile)
    ZanataVer=latest
fi

echo "Preparing container for Zanata ($ZanataVer)"

## Create zanata-files volume if it is missing
if ! (docker volume ls -q | grep zanata-files) ; then
    docker volume create --name zanata-files
fi

: ${ZANATA_PORT:=8080}
DockerOptArray=(--name zanata -v zanata-files:/var/lib/zanata -e ZANATA_HOME=/var/lib/zanata --link zanatadb:db -p $ZANATA_PORT:8080)

## If specified ZANATA_DAEMON_MODE=1, it runs Zanata as daemon,
## Otherwise it will remove the container after program exit.
if [ "${ZANATA_DAEMON_MODE-}" = "1" ];then
    DockerOptArray+=( -d )
else
    DockerOptArray+=( --rm  -it )
fi

## Setup DB container if not running
if [ -z  $(docker ps -aq -f name=zanatadb -f status=running) ]; then
    $ScriptDir/rundb.sh
fi

docker run ${DockerOptArray[@]} zanata/server:$ZanataVer
