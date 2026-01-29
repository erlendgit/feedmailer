#!/usr/bin/env bash

ORIGINAL_DIR="$(pwd)"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$SCRIPT_DIR"
./bin/setup.sh

cd "$ORIGINAL_DIR"
"$SCRIPT_DIR/venv/bin/python3" "$SCRIPT_DIR/main.py" "$@"
