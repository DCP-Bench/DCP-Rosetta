#!/bin/sh
# usage: run.sh probe.py [args]
d=$(cd "$(dirname "$0")" && pwd); f=$1; shift
docker run --rm --network none -v "$d":/p:ro --entrypoint python dcp-eval/yices_python:v1 /p/"$f" "$@"
