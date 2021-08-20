#!/bin/bash

# 
# mostly a dev script
# creates a new search index from the data you already have in postgres
#
# (nice to have, if you want to mess up your search index, but dont want to pull the data everytime)
#

set -e
set -x

source .env

$DOCKER_COMPOSE -f ${DOCKERFILE} up -d postgres service

# import new data from indexer
# create new search index, rotate search index
$DOCKER_COMPOSE -f ${DOCKERFILE} run --rm manticore /bin/sh -c "HUBGREP_NEW_REPO_TABLE_NAME=repositories indexer --all"


