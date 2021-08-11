#!/bin/bash

# 
# everything that needs to be done to update the search index on the fly
#

set -e
set -x

source .env

temp_table_name=new_repositories


$DOCKER_COMPOSE -f ${DOCKERFILE} up -d sphinx postgres service

# import new data from indexer
$DOCKER_COMPOSE -f ${DOCKERFILE} exec service /bin/bash -ic "flask cli import-repos ${temp_table_name}"

# create new search index, rotate search index
# (todo: table name is hardcoded in sphinx.conf for now...)
$DOCKER_COMPOSE -f ${DOCKERFILE} exec sphinx cat /opt/sphinx/conf/sphinx.conf
# todo: if data is empty: docker-compose run sphinx indexer --all --config /opt/sphinx/conf/sphinx.conf --rotate
$DOCKER_COMPOSE -f ${DOCKERFILE} exec sphinx indexer --all --config /opt/sphinx/conf/sphinx.conf --rotate

$DOCKER_COMPOSE -f ${DOCKERFILE} exec service /bin/bash -ic "flask cli rotate-repositories-table ${temp_table_name}"
