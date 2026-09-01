#!/usr/bin/env bash
set -e
base="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
exec sumide "$base/hello.py" "$base/hello.R" "$base/hello.sh" "$base/hello.c" "$base/hello.cpp"
