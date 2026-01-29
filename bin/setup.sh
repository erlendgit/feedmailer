#!/usr/bin/env bash

if [[ -z $(python --version) ]]; then
  echo "python executable not found"
  exit 1
fi

if [[ ! -d venv ]]; then
  python -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
else
  source venv/bin/activate
fi

