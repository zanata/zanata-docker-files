#!/bin/bash -eu
ScriptDir=$(dirname $(readlink -f $0))
ZanataVer=$(sed -n -e '/^ARG\s*ZANATA_VERSION/ s/^ARG\s*ZANATA_VERSION\s*=\s*\(.*\)\s*/\1/p' < $ScriptDir/Dockerfile)
docker run --rm --name zanata --link zanatadb:db -p 8080:8080 -it zanata/server:$ZanataVer
