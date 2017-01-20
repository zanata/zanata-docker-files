# Zanata Docker Images

Docker images for Zanata project.

## Release Docker Image
Release docker image includes build, tag, and push the docker images.
In order to be able to perform above tasks, you need to login to an docker
account.

### Login to docker hub Account
If you do not have a docker hub account, register one at:
https://hub.docker.com/

and ask the Zanata team members to add you to Zanata team.

You also need to login from the command line at your workstation,
so you can push the image to docker hub.
Run the following command and enter the docker registry username and
password:

```sh
docker login docker.io
```

### Make Image

The program `./image-make` releases the docker images to docker hub.

Run `./image-make -h` for the usage.

For releasing a zanata-server docker image, run:
```sh
./image-make -t latest -t <version> -p zanata-server
```

For example, run the following when release 4.0.1 as latest, and push to docker
hub:
```
./image-make -t latest -t 4.0.1 -p zanata-server
```

If you find yourself need to change the Dockerfile, but you don't want to wait
for another platform release, then add '-1' after the version, like

```
./image-make -t latest -t 4.0.1-1 -p zanata-server
```

If you need to change Dockerfile again, then bump the sub version to -2, and so
on.


_Note: These images are provided on a best-effort basis. Pull requests are most welcome_

Please report any issues in Zanata's bug tracker: https://zanata.atlassian.net/
