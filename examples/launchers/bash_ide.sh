#!/usr/bin/env bash
set -e
base="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
exec sumbash "${1:-$base/hello.sh}"
