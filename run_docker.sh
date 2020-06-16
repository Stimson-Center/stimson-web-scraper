#!/bin/sh

docker system prune --force
docker build -t stimson-web-scraper . 
docker run --user seluser -p 3000:3000 -p 5000:5000 -it stimson-web-scraper
