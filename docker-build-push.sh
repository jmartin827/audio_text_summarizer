#!/bin/bash

# Docker or container registry name
name=$1

# TODO review and refactor
#docker buildx create --name mybuilder

## TODO debug issues with amd64 image size for whisper ai using buildx
#platforms="linux/arm64"
platforms="linux/amd64"
tag="${platforms#*/}"



docker buildx build --push --platform $platforms -t "$name"/celery:"$tag" ./celery_worker
docker buildx build --push --platform $platforms -t "$name"/celery-remote:"$tag" ./celery_remote
docker buildx build --push --platform $platforms -t "$name"/fast-api:"$tag" ./fast_api

## Build the reactjs app locally and copy build file into nginx container
npm install --prefix ./front_end
npm run build --prefix ./front_end
docker buildx build --push --platform $platforms -t "$name"/front_end:"$tag" ./front_end
