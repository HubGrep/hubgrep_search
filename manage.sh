#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

set -o allexport
source $DIR/.env
set +o allexport


USAGE="$0 COMMAND

COMMANDs
build         -  build project files needed for deployment
test          -  run tests
bumpversion [patch|minor|major] [--dry-run]
              -  bump the version number
"


function bumpversion() {
    local part=$1
    local dry_run_arg=$2

    if ! [[ "$part" =~ ^(patch|minor|major)$ ]]; then
        echo "part must be one of [patch|minor|major]"
        exit 1
    fi
    
    case $dry_run_arg in
        "--dry-run")
            dry_run="--dry-run --allow-dirty"
            ;;
        *)
            echo "unknown argument $dry_run_arg"
            exit 1
    esac
    
    bump2version $part $dry_run --verbose
}


if [ -z "$1" ]; then
  echo "usage: $USAGE"
  exit 0
else

  if [ "$1" == "build" ]; then
    APP_ENV="build" flask cli build-scss
  elif [ "$1" == "test" ]; then
    echo "running tests..."
    pytest --cov=hubgrep .
  elif [ "$1" == "bumpversion" ]; then
    shift
    bumpversion $@
  else
    echo "usage: $USAGE"
  fi
fi

shift
