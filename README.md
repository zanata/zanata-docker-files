# Zanata Docker Images

Docker images for Zanata project.

## Release Docker Image
The task to release a docker image includes the following steps: build, 
tag, and push.
In order to be able to perform the above, you need to log in to a Docker
account.

### Login to docker hub Account
If you do not have a Docker Hub account, register at
https://hub.docker.com/ then ask the Zanata team members to add you.

You also need to login from the command line at your workstation,
so you can push the image to Docker Hub.
Run the following command and enter the docker registry username and
password:

```sh
docker login docker.io
```

### Make Image

The program `./image-make` releases the docker images to Docker Hub.

Run `./image-make -h` for usage.

To release a zanata-server docker image, run:
```sh
./image-make -t latest -t <version> -p zanata-server
```

For example, run the following when release 4.0.1 is the latest, and push to Docker Hub:
```
./image-make -t latest -t 4.0.1 -p zanata-server
```

If you need to change the Dockerfile, but you don't want to wait
for another platform release, then add '-1' after the version:

```
./image-make -t latest -t 4.0.1-1 -p zanata-server
```

If you need to change the Dockerfile again, then bump the sub version to -2, and so on.


_Note: These images are provided on a best-effort basis. Pull requests are most welcome_

Please report any issues in Zanata's bug tracker: https://zanata.atlassian.net/
