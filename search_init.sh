#!/bin/bash

# 
# everything that needs to be done for the first start
#
# manticores searchd wont start until it has a first index,
# so we need to start up postgres, fill it with a backup that we pull
# from the indexer, and create a first index.
#
# if you already have an index, you most likely want to run ./search_update.sh instead.
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
$DOCKER_COMPOSE -f ${DOCKERFILE} run --rm manticore indexer --all
$DOCKER_COMPOSE -f ${DOCKERFILE} up -d manticore

# rotate db tables
$DOCKER_COMPOSE -f ${DOCKERFILE} exec service /bin/bash -ic "flask cli rotate-repositories-table $HUBGREP_NEW_REPO_TABLE_NAME"

# start everything!
$DOCKER_COMPOSE -f ${DOCKERFILE} up -d

