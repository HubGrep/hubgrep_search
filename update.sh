#!/bin/bash

set -e
set -x

docker_compose=docker-compose  #/usr/local/bin/docker-compose



#$docker_compose run service flask cli import-repos

# todo: import to new table, create index from new table, then rotate both, delete old one

$docker_compose up -d sphinx postgres
$docker_compose exec sphinx cat /opt/sphinx/conf/sphinx.conf
$docker_compose exec sphinx indexer --all --config /opt/sphinx/conf/sphinx.conf --rotate

