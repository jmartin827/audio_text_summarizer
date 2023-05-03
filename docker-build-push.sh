#!/bin/bash

# Docker or container registry name
name=$1

# TODO review and refactor
#docker buildx create --name mybuilder

## TODO debug issues with amd64 image size for whisper ai using buildx
#platforms="linux/amd64"
#--platform $platforms


docker buildx build --push -t "$name"/celery:test ./celery_worker
docker buildx build --push -t "$name"/celery-remote:test ./celery_remote
docker buildx build --push -t "$name"/fast-api:test ./fast_api
