#!/bin/bash

make build
docker-compose down
docker-compose build
docker-compose up -d
