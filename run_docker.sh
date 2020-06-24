#!/usr/bin/env bash

docker system prune --force
docker build -t stimson-web-scraper . 
docker run -it -v `pwd`:/mnt --entrypoint=/bin/bash  stimson-web-scraper
