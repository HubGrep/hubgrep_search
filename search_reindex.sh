#!/bin/bash

# 
# everything that needs to be done to update the search index on the fly
#

set -e
set -x

source .env

$DOCKER_COMPOSE -f ${DOCKERFILE} up -d postgres service

# import new data from indexer
# create new search index, rotate search index
$DOCKER_COMPOSE -f ${DOCKERFILE} run --rm manticore /bin/sh -c "HUBGREP_NEW_REPO_TABLE_NAME=repositories indexer --all"


