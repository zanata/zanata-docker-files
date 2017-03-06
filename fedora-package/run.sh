#!/bin/bash

echo === building the image...
docker build -t fedorareview .

echo === finish building the image
echo === running the container...
docker run --name fedorareview --rm -it --cap-add=SYS_ADMIN fedorareview mock

