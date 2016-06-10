This is a docker image for the Zanata server. This image runs a wildfly server with Zanata running on top of it. It does not run a database server for the Zanata application

```
This image has been tested with Docker 1.8
```

## Building

To build this docker image, simply type the following command:

```sh
$ docker build -t zanata/server:$VERSION .
```

Replace $VERSION with the version you want to tag, eg 3.8.4. Be careful about overwriting existing versions.

The `-t` parameter indicates a tag for the image.

## Running a Zanata server with Docker

### Run a database server image

Pull the mariadb docker image:

```sh
$ docker pull fedora/mariadb
```

Run the maria db server container specifying the following parameters:

`--name`: The name of the docker container (will be used later)

`-e USER=username`: The database username

`-e PASS=password`: The database password for the username above

`-e NAME=dbname`: The name of the database

For example:

```sh
$ docker run --name=zanatadb -e USER=zanata -e PASS=zanata -e NAME=zanata -d -p 3306:3306 fedora/mariadb
```

The command above starts a docker container running mariadb for a database called `zanata` and exposes port 3306 to the outside of the container. The server will take a few minutes to initialize the database and start.

## Run the Zanata (Wildfly) server image

Run the following command to start the wildfly container with Zanata in tow. It will link the database container (`--link`) named `zanatadb` (same name which was given to the database container above) to the alias `db`.

```sh
$ docker run -it -P --link=zanatadb:db zanata/server:$VERSION
```

Replace $VERSION with the version you want to run, eg 3.8.4. Check DockerHub for available versions.


## Create an admin user

At this point, you have a running Zanata instance... with no users created (!)

To create an admin user, you can connect to the database server and run the script at `/conf/admin-user-setup.sql` like this:

```sh
$ mysql --protocol=tcp -h $IP_ADDRESS -u zanata -p zanata < admin-user-setup.sql
```

where `IP_ADDRESS` is the docker host's address (this might be localhost or some other IP address if running on OSX for example)

This will create a username `admin` with password `admin1234`

## Access Zanata

The docker host  will forward a random port to the container's 8080 port where Wildfly is listening. To find out which port it is being forwarded from just type the following command on the docker host:

```sh
$ docker ps
```

and look at the `PORTS` column. It should tell you which port is being forwarded to port 8080 on the container.

Just open a browser and head to `http://IP_ADDRESS:PORT/zanata`, where `PORT` is the port determined in the previous step, and `IP_ADDRESS` is the docker host's address (again, this might localhost or some other IP address if running on OSX for example).

## DockerHub

The DockerHub site for Zanata images is here:
https://hub.docker.com/r/zanata/server/
