#!/bin/sh
docker run --name zanata --link zanatadb:db -it zanata/server:3.8.4
