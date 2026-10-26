#!/bin/bash
# usage: smoke.sh model.c request-json  (runs the image like the evaluator does)
d=$(mktemp -d); cp "$1" $d/model.c; echo "$2" > $d/request.json; chmod -R a+rX $d
docker run --rm --network none --read-only --user 65534:65534 --cap-drop ALL --security-opt=no-new-privileges --tmpfs /tmp:rw,exec,nosuid,size=536870912,mode=1777 -v $d:/input:ro dcp-eval/yices_c:v1
