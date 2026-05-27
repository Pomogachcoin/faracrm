#!/bin/bash
set -e
cd /opt/faracrm

echo === DEPLOY PROD ===
echo Pulling from origin crimpal-prod...
git pull origin crimpal-prod

echo Building containers...
docker compose build

echo Restarting services...
docker compose up -d

echo === DONE: https://crm.crimpalsert.ru ===
