#!/bin/sh
docker run --name zanata --link zanatadb:db -p 8080:8080 -it zanata/server:3.9.0
