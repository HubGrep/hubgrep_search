#!/bin/bash

set -e
set -x

docker_compose=docker-compose  #/usr/local/bin/docker-compose
temp_table_name=temp_repositories


$docker_compose up -d sphinx postgres service

# import new data from indexer
$docker_compose exec service /bin/bash -ic "flask cli import-repos ${temp_table_name}"

# create new search index, rotate search index
# (todo: table name is hardcoded in sphinx.conf for now...)
$docker_compose exec sphinx cat /opt/sphinx/conf/sphinx.conf
# todo: if data is empty: docker-compose run sphinx indexer --all --config /opt/sphinx/conf/sphinx.conf --rotate
$docker_compose exec sphinx indexer --all --config /opt/sphinx/conf/sphinx.conf --rotate

$docker_compose exec service /bin/bash -ic "flask cli rotate-repositories-table ${temp_table_name}"
