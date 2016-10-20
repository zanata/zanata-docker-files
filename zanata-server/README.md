This document shows how to set up a Zanata instance using docker.

The helper scripts use docker data volumes, therefore docker &gt;= 1.9
is required.

Assume you have checkout this repository, and `cd zanata-server`.

## Build Image
This section is for developers who want to build images.
Skip to next section if you just want to use Zanata.

To build the latest released Zanata server, run the following command:
```sh
$ docker build -t zanata/server . 
```

You can also specify version you want to build, for example, 3.9.5, with following command:
```sh
$ docker build -t zanata/server:3.9.5 --build-arg=ZANATA_VERSION=3.9.5 . 
```

Note that for older version, you may need to edit `standalone.xml` to make Zanata works.

## Setup Environment
Those environment variables are used in helper scripts.
Override them to suit your need.

* `ZANATA_MYSQL_DATABASE`: Zanata uses this database name in MariaDB. (Default: `zanata`)
* `ZANATA_MYSQL_USER`: Zanata uses this username to access database in MariaDB. (Default: `zanata`)
* `ZANATA_MYSQL_PASSWORD`: Zanata uses this password to access database in MariaDB. (Default: `password`)
* `ZANATA_PORT`: Zanata listens this port on the host. (Default: `8080`)
* `ZANATA_DAEMON_MODE`: If non empty, the Zanata is run as daemon, otherwise, it runs in frontend and print log to console. (Default: `1`)
* `ZANATA_VERSION`: Zanata version to be run. If not specified, it uses the ZANATA_VERSION specified in `Dockerfile`.

## Run Database as docker container

Zanata uses MariaDB or MySQL as database backend. 
We recommended to run the database service in docker as well.
To setup and start the database service, run:
```sh
./rundb.sh
```

## Run Zanata as docker container
Run the following command to start the wildfly container with Zanata in tow. It will link the database container (`--link`) named `zanatadb` (same name which was given to the database container above) to the alias `db`.
```sh
./runapp.sh
```

## Create an admin user

At this point, you have a running Zanata instance... with no users created (!)

To create an admin user, you can connect to the database server and run the script at `conf/admin-user-setup.sql` like this:

```sh
$ DB_IP=$(docker inspect ---format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' zanatadb)
$ mysql --protocol=tcp -h $DB_IP -u zanata -p zanata < conf/admin-user-setup.sql
```

where `DB_IP` is IP address of `zanatadb`. You do need to type the Zanata Maridb password
(defined in `ZANATA_MYSQL_PASSWORD`, default is `password`).

## Access Zanata
Open a browser and head to `http://HOST:PORT/zanata`, where `PORT` is the port determined in the previous step, and `HOST` is the docker host's address (this might be `localhost` or some other IP address if running on OSX for example).

In other words, if you run Zanata in your local machine and change nothing,
you can reach Zanata at `http://localhost:8080/zanata`

## DockerHub

The DockerHub site for Zanata images is here:
https://hub.docker.com/r/zanata/server/
