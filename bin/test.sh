#!/usr/bin/env bash

if [[ -z "$@" ]]; then
  python -m unittest discover -s "$TEST_MATCH" -p "*.py"
else
  python -m unittest "$@"
fi
