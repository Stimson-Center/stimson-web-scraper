#!/usr/bin/env bash

docker system prune --force
docker build -t stimson-web-scraper . 
docker run -it --entrypoint=/bin/bash  stimson-web-scraper
