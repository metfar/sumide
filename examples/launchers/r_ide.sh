#!/usr/bin/env bash
set -e
base="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
exec sumr "${1:-$base/hello.R}"
