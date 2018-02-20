This document shows how to set up a Zanata instance using docker.

The helper scripts use docker data volumes and docker container network, therefore docker &gt;= 1.9
is required.

The following instructions assume that you have cloned this repository
and opened a terminal in the zanata-server directory.

## Build Image
This section is for developers who want to build images.
Skip to next section if you just want to use Zanata.

To build the latest released Zanata server, run the following command:
```sh
$ docker build -t zanata/server .
```

You can also specify the version you want to build. For example, you can build version 4.2.1 with the following command:
```sh
$ docker build -t zanata/server:4.2.1 --build-arg=ZANATA_VERSION=4.2.1 .
```

Note that for older versions, you may need to edit `standalone.xml` to make Zanata work.

## Setup Environment
These environment variables are used in the helper scripts.
Override them to suit your needs.

* `ZANATA_DAEMON_MODE`:
   If `1`, the Zanata runs as daemon;
   otherwise, it runs in the foreground and prints its log directly to the console. (Default: empty )
* `ZANATA_DOCKER_NETWORK`: docker network that Zanata containers belong. (Default: `docker-network`)
* `ZANATA_MGMT_PORT`: Wildfly management port. (Default: 9990)
* `ZANATA_MYSQL_DATABASE`: Zanata uses this database name in MariaDB. (Default: `zanata`)
* `ZANATA_MYSQL_USER`: Zanata uses this username to access database in MariaDB. (Default: `zanata`)
* `ZANATA_MYSQL_PASSWORD`: Zanata uses this password to access database in MariaDB. (Default: `password`)
* `ZANATA_PORT`: Zanata listens on this port on the host. (Default: `8080`)
* `ZANATA_VERSION`: Zanata docker version to be run. (Default: `latest`)
* `ZANATA_MAIL_HOST`: SMTP host Zanata will send mails to. (Default: `localhost`)
* `ZANATA_MAIL_PORT`: SMTP port Zanata will send mails to. (Default: `25`)
* `ZANATA_MAIL_USERNAME`: SMTP Username for mail authentication (Default: `username`)
* `ZANATA_MAIL_PASSWORD`: SMTP Password for mail authentication (Default: `password`)
* `ZANATA_MAIL_TLS`: Enable TLS transport for SMTP (Default: `false`)
* `ZANATA_MAIL_SSL`: Enable SSL transport for SMTP (usually used on Port 465) (Default: `false`)

## Run Zanata as docker container
To run Zanata as docker container, set up your config as environment variables (see above) in a .env file.

Then simply run:
```
./runapp.sh
```

If the data containers are not running, this will start the data containers as well.
See `rundb.sh` for the invocation detail.


## Create an admin user

At this point, you have a running Zanata instance... with no users created (!)

To create an admin user, you can connect to the database server and run the script at `conf/admin-user-setup.sql` like this:

```sh
$ DB_IP=$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' zanatadb)
$ mysql --protocol=tcp -h $DB_IP -u zanata -p zanata < conf/admin-user-setup.sql
```

where `DB_IP` is IP address of `zanatadb`. You will need to type the Zanata Maridb password
(defined in `ZANATA_MYSQL_PASSWORD`, default is `password`).

This won't work if you haven't installed mysql locally and the zanatadb port isn't exposed.
To run the script alternatively direct inside of the container please first copy the admin-user-setup.sql file to the container and then run mysql inside of the container:

```sh
$ docker cp conf/admin-user-setup.sql zanatadb:/tmp
$ docker exec -it zanatadb bash -c "mysql -u zanata --password=password zanata < /tmp/admin-user-setup.sql"
```

## Access Zanata
Open a browser and head to `http://HOST:PORT/zanata`, where `PORT` is the port specified in `ZANATA_HOST_PORT` (default `8080`), and `HOST` is the docker host's address (this might be `localhost` or some other IP address if running on OSX for example).

In other words, if you run Zanata in your local machine and change nothing,
you can reach Zanata at `http://localhost:8080/zanata`

## DockerHub

The DockerHub site for Zanata images is here:
https://hub.docker.com/r/zanata/server/
