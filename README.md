# Zanata Docker Files

This repository includes files that are necessary to build docker images for Zanata.

 * [zanata-server](zanata-server/README.md): Zanata Server docker image.
 * [fedora-package](fedora-package/): For Fedora package review and build.
 * [image-make](image-make): Script to build non-zanata-server docker images .
 * [DockerHelper.py](DockerHelper.py): Script to build zanata-server docker images.

For people who are in charge of publishing Zanata docker images,
or interested in customizing Zanata docker images, read on.

## Publish Zanata Docker Images
Publish means to build, tag and push images to registry.
Note that only Zanata team is able to publish Zanata docker images

Firstly, clone this repository and `cd` into the checked out directory.
Then, login to docker from command line:
```sh
docker login
```
If you do not have docker login yet, see section **Login to docker hub Account**.

So far, we have `DockerHelper.py` (new script) for zanata-server, and
`image-make` (old script) for everything else.

### Publish zanata-server Docker Images
Use `DockerHelper.py` to publish the zanata-server images.

For usage:
```sh
./DockerHelper.py -h
```

Usually, we can just publish images with 'auto' setting.
```sh
./DockerHelper.py publish server auto
```
It basically means use the latest released zanata-platform version and the next postrelease number.

The **postrelease** number is the number that indicates the changes on the `zanata-docker-files`
including changes `Dockerfile` and configuration associated with production docker images.
It start as 1 when it is built for the first time for the released zanata-platform version.

For example, `4.4.3-1` means it is the first docker image build against version 4.4.3.

You can also specify the tag like:
```sh
./DockerHelper.py publish server 4.4.3-2
```

### Publish other Docker Images
Use `image-make` to build the non-zanata-server image.

For usage:
```sh
./image-make -h
```

To publish the image from centos-repo-builder:
```sh
./image-make -p centos-repo-builder
```

### Login to docker hub Account
If you do not have a Docker Hub account, register at
https://hub.docker.com/ then ask other Zanata team members to add you.

You also need to login from the command line at your workstation,
so you can push the image to Docker Hub.

Run the following command and enter the docker registry username and password:
```sh
docker login docker.io
```


_Note: These images are provided on a best-effort basis. Pull requests are most welcome_

Please report any issues in Zanata's bug tracker: https://zanata.atlassian.net/
