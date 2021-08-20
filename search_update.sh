#!/bin/bash

# 
# everything that needs to be done to update the search index on the fly
#
# fetch a new export of the indexer data and update postgres and the search index.
# you may want to set up cron to run this script for you.
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
