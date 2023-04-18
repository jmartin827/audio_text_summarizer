#!/bin/bash

# Get the name from the command line argument
name=$1

cd celery_worker && docker build -t "$name"/celery:test . && docker push "$name"/celery:test
cd ../fast_api && docker build -t "$name"/fast-api:test . && docker push "$name"/fast-api:test