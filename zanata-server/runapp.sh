#!/bin/bash -eu

ScriptFile=$(realpath ${BASH_SOURCE[0]})
ScriptDir=$(dirname $ScriptFile)
source $ScriptDir/common

# misc
JBOSS_DEPLOYMENT_VOLUME=/opt/jboss/wildfly/standalone/deployments/

if [ -n "${ZANATA_VERSION-}" ];then
    ## Use the version from set environment ZANATA_VERSION
    ZanataVer=$ZANATA_VERSION
else
    ## Use the latest version (not necessarily the version defined in the Dockerfile)
    ZanataVer=latest
fi

declare -a DockerOptArray
while getopts "e:p:n:hl:" opt; do
    case ${opt} in
        e)
            echo "==== use $OPTARG as mail host ===="
            ZANATA_MAIL_HOST=$OPTARG
            ;;
        l)
            echo "==== provide SMTP host login (username:password) ===="
            # set the internal field separator (IFS) variable, and then let it parse into an array.
            # When this happens in a command, then the assignment to IFS only takes place to that single command's environment (to read ).
            # It then parses the input according to the IFS variable value into an array
            IFS=':' read -ra CREDENTIAL <<< "$OPTARG"
            if [ ${#CREDENTIAL[@]} -ne 2 ]; then
                echo "Must provide SMTP credentials in username:password format (colon separated)"
                exit 1
            fi
            ZANATA_MAIL_USERNAME=${CREDENTIAL[0]}
            ZANATA_MAIL_PASSWORD=${CREDENTIAL[1]}
            DockerOptArray+=( -e MAIL_USERNAME="${ZANATA_MAIL_USERNAME}" -e MAIL_PASSWORD="${ZANATA_MAIL_PASSWORD}" )
            ;;
        p)
            echo "===== set JBoss port offset to $OPTARG ====="
            if [ "$OPTARG" -eq "$OPTARG" ] 2>/dev/null
            then
                ZANATA_PORT=$(($OPTARG + 8080))
                ZANATA_DEBUG_PORT=$(($OPTARG + 8787))
                ZANATA_MGMT_PORT=$(($OPTARG + 9090))
                echo "===== Zanata HTTP port : $ZANATA_PORT"
                echo "===== Debug port       : $ZANATA_DEBUG_PORT"
                echo "===== Management port  : $ZANATA_MGMT_PORT"
            else
                echo "===== MUST provide an integer as argument ====="
                exit 1
            fi
            ;;
        n)
            echo "===== set docker network to $OPTARG ====="
            ZANATA_DOCKER_NETWORK=$OPTARG
            ;;
        h)
            echo "========   HELP   ========="
            echo "-e <SMTP email host>  : SMTP mail host"
            echo "-l <username:password>: SMTP login: username and password separated by colon"
            echo "-p <offset number>    : set JBoss port offset"
            echo "-n <docker network>   : will connect container to given docker network (default is $ZANATA_DOCKER_NETWORK)"
            echo "-h                    : display help"
            exit
            ;;
        \?)
            echo "Invalid option: -${OPTARG}. Use -h for help" >&2
            exit 1
            ;;
    esac
done

## Checking Variables
if [[ -z ${ZANATA_MAIL_HOST:-} ]];then
    echo "[ERROR] Undefined mail host. Use Option -e <mailHost> or environment variable ZANATA_MAIL_HOST=<mailHost>" > /dev/stderr
    exit 1
fi

ensure_docker_network

## Setup DB container if not running
if [ -z  $(docker ps -aq -f name=zanatadb -f status=running) ]; then
    $ScriptDir/rundb.sh
fi
ZANATA_DB_HOST=$(docker inspect  --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' zanatadb)

echo "Preparing container for Zanata ($ZanataVer)" > /dev/stderr
## Create zanata-files volume if it is missing
if ! (docker volume ls -q | grep zanata-files) ; then
    docker volume create --name zanata-files
fi

DockerOptArray+=( --name zanata
   -e DB_USERNAME="${ZANATA_MYSQL_USER}" \
   -e DB_PASSWORD="${ZANATA_MYSQL_PASSWORD}" \
   -e DB_SCHEMA="${ZANATA_MYSQL_DATABASE}" \
   -e DB_HOSTNAME="${ZANATA_DB_HOST}" \
   -e MAIL_HOST="${ZANATA_MAIL_HOST}" \
   -e MAIL_PORT="${ZANATA_MAIL_PORT}" \
   -e MAIL_USERNAME="${ZANATA_MAIL_USERNAME:= }" \
   -e MAIL_PASSWORD="${ZANATA_MAIL_PASSWORD:= }" \
   -e MAIL_TLS="${ZANATA_MAIL_TLS}" \
   -e MAIL_SSL="${ZANATA_MAIL_SSL}" \
   -e ZANATA_HOME=/var/lib/zanata \
   -e ZANATA_MGMT=${ZANATA_MGMT_PORT} \
   --net ${ZANATA_DOCKER_NETWORK} \
   -p ${ZANATA_PORT}:8080 \
   -p ${ZANATA_DEBUG_PORT}:8787 \
   -v zanata-files:/var/lib/zanata:Z \
   )

## If specified ZANATA_DAEMON_MODE=1, it runs Zanata as daemon,
## Otherwise it will remove the container after program exit.
if [ "${ZANATA_DAEMON_MODE-}" = "1" ];then
    DockerOptArray+=( -d )
else
    DockerOptArray+=( --rm  -it )
fi

docker run ${DockerOptArray[@]} zanata/server:$ZanataVer
