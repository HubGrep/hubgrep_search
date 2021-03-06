#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
source $DIR/.env

echo "$1"

USAGE="$0 COMMAND

COMMANDs
build          build project files needed for deployment
test           run tests
"

if [ -z "$1" ]; then
  echo "usage: $USAGE"
  exit 0
else

  if [ "$1" == "build" ]; then
    echo "building... TODO =("
  elif [ "$1" == "test" ]; then
    echo "running tests..."
    pytest --cov=hubgrep .
  else
    echo "usage: $USAGE"
  fi
fi

shift