#!/bin/bash

# 
# everything that needs to be done for the first start
#

set -e
set -x

source .env

temp_table_name=new_repositories

# sphinx doesnt like being started without having an index,
# so we skip it here and only start postgres and hubgrep
$DOCKER_COMPOSE -f ${DOCKERFILE} up -d postgres service

# initialize postgres db
$DOCKER_COMPOSE -f ${DOCKERFILE} exec service /bin/bash -ic "flask db upgrade"

# import new data from indexer
$DOCKER_COMPOSE -f ${DOCKERFILE} exec service /bin/bash -ic "flask cli import-repos ${temp_table_name}"

# create the first search index and start sphinx afterwards
$DOCKER_COMPOSE -f ${DOCKERFILE} run sphinx cat /opt/sphinx/conf/sphinx.conf
$DOCKER_COMPOSE -f ${DOCKERFILE} run sphinx indexer --all --config /opt/sphinx/conf/sphinx.conf
$DOCKER_COMPOSE -f ${DOCKERFILE} up -d sphinx

# rotate db tables
$DOCKER_COMPOSE -f ${DOCKERFILE} exec service /bin/bash -ic "flask cli rotate-repositories-table ${temp_table_name}"

# start everything!
$DOCKER_COMPOSE -f ${DOCKERFILE} up -d

