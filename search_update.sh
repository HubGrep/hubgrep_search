#!/bin/bash

# 
# everything that needs to be done to update the search index on the fly
#

set -e
set -x

source .env

$DOCKER_COMPOSE -f ${DOCKERFILE} up -d manticore postgres service

# import new data from indexer
$DOCKER_COMPOSE -f ${DOCKERFILE} exec service /bin/bash -ic "flask cli import-repos $HUBGREP_NEW_REPO_TABLE_NAME"

# create new search index, rotate search index
$DOCKER_COMPOSE -f ${DOCKERFILE} exec manticore indexer --all --rotate

$DOCKER_COMPOSE -f ${DOCKERFILE} exec service /bin/bash -ic "flask cli rotate-repositories-table $HUBGREP_NEW_REPO_TABLE_NAME"
