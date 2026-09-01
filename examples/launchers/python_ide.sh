#!/usr/bin/env bash
set -e
base="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
exec sumpy "${1:-$base/hello.py}"
