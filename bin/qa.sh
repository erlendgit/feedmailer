#!/usr/bin/env bash


export ruff="venv/bin/ruff --config=pyproject.toml"

$ruff check . --fix
$ruff format .