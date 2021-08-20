#!/bin/bash

# 
# everything that needs to be done for the first start
#

set -e
set -x

source .env

# sphinx doesnt like being started without having an index,
# so we skip it here and only start postgres and hubgrep
$DOCKER_COMPOSE -f ${DOCKERFILE} up -d postgres service

# initialize postgres db
$DOCKER_COMPOSE -f ${DOCKERFILE} exec service /bin/bash -ic "flask db upgrade"

# import new data from indexer
$DOCKER_COMPOSE -f ${DOCKERFILE} exec service /bin/bash -ic "flask cli import-repos $HUBGREP_NEW_REPO_TABLE_NAME"

# create the first search index and start sphinx afterwards
$DOCKER_COMPOSE -f ${DOCKERFILE} run sphinx cat /opt/sphinx/conf/sphinx.conf
$DOCKER_COMPOSE -f ${DOCKERFILE} run sphinx indexer --all --config /opt/sphinx/conf/sphinx.conf
$DOCKER_COMPOSE -f ${DOCKERFILE} up -d sphinx

# rotate db tables
$DOCKER_COMPOSE -f ${DOCKERFILE} exec service /bin/bash -ic "flask cli rotate-repositories-table $HUBGREP_NEW_REPO_TABLE_NAME"

# start everything!
$DOCKER_COMPOSE -f ${DOCKERFILE} up -d

