#!/usr/bin/env bash
set -e
base="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
exec sumcxx "${1:-$base/hello.cpp}"
