# Zanata Docker Images

Docker images for Zanata project.

## Release docker image

The program `./image-make` builds and push the image to docker hub.

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
