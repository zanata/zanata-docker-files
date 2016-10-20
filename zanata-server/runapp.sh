#!/bin/bash -eu
ScriptDir=$(dirname $(readlink -f $0))
if [ -n "${ZANATA_VERSION-}" ];then
    ZanataVer=$ZANATA_VERSION
else
    ZanataVer=$(sed -r -n -e '/^ARG\s+ZANATA_VERSION/ s/^ARG\s+ZANATA_VERSION\s*=\s*(.*)\s*/\1/p' < $ScriptDir/Dockerfile)
fi

: ${ZANATA_PORT:=8080}
DockerOptArray=(--name zanata --volumes-from zanatadb -v zanatadb:/opt/jboss --link zanatadb:db -p $ZANATA_PORT:8080)

## If specified ZANATA_DAEMON_MODE=1, it runs Zanata as daemon,
## Otherwise it will remove the container after program exit.
if [ -n "${ZANATA_DAEMON_MODE-}" ];then
    DockerOptArray+=( -d )
else
    DockerOptArray+=( --rm  -it )
fi

## Setup DB container if not running
if [ -z  $(docker ps -aq -f name=zanatadb -f status=running) ]; then
    $ScriptDir/rundb.sh
fi

docker run ${DockerOptArray[@]} zanata/server:$ZanataVer
