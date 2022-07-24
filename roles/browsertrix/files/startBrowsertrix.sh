#!/bin/bash
cd /root/browsertrix
source configs/config.env
docker stack deploy \
-c /root/browsertrix/docker-compose.yml \
-c /root/browsertrix/configs/docker-compose.swarm.yml \
-c /root/browsertrix/configs/docker-compose.signing.yml \
-c /root/browsertrix/docker-compose.override.yml btrix