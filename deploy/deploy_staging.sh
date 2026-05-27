#!/bin/bash
set -e
cd /opt/faracrm

echo === DEPLOY STAGING ===
echo Pulling from origin crimpal-prod...
git pull origin crimpal-prod

echo Building staging containers...
docker compose -f docker-compose.staging.yml build

echo Restarting staging services...
docker compose -f docker-compose.staging.yml up -d

echo === DONE: http://185.244.51.110:8081 ===
