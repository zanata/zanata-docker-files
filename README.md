# Zanata Docker Files

This repository includes files that are necessary to build docker images for Zanata.

 * [zanata-server](zanata-server/README.md): Zanata Server docker image.
 * [fedora-package](fedora-package/): For Fedora package review and build.
 * [image-make](image-make): Script to build docker images.

For people who are in charge of publishing Zanata docker images,
or interested in customizing Zanata docker images, read on.

## Build Zanata Docker Images
Firstly, clone this repository and `cd` into the checked out directory.

Then, use `image-make` to build the image.

For usage:
```sh
./image-make -h
```

To build the version `4.3.0` and tag it as latest:
```sh
./image-make -t latest -t 4.3.0 zanata-server
```

## Zanata Docker Image Releasing
Zanata docker image release are made by Zanata team members.

### Login to docker hub Account
If you do not have a Docker Hub account, register at
https://hub.docker.com/ then ask other Zanata team members to add you.

You also need to login from the command line at your workstation,
so you can push the image to Docker Hub.

Run the following command and enter the docker registry username and password:
```sh
docker login docker.io
```

### Update Dockerfile
If you only need to change the version, no need to change the Dockerfile manually,
`image-make` takes care of this.

If you do need to change more than version, remember in next step,
you need to append sequence number '-1' after the version. For example,
if you change Dockerfile after version 4.3.0, then you need to tag
the image as `4.3.0-1`.

If you need to change the Dockerfile again, then bump the sequence number to -2, and so on.

### Release Image to DockerHub
Script `image-make` with option `-r` releases image to DockerHub. For example,
to release zanata-server `4.3.0-1`, run:

```sh
./image-make -r 4.3.0-1 zanata-server
```

See the in-line help for the actual behavior of `./image-make -r` by running:
```sh
./image-make -h
```

_Note: These images are provided on a best-effort basis. Pull requests are most welcome_

Please report any issues in Zanata's bug tracker: https://zanata.atlassian.net/
