#!/bin/bash
f=/root/deploy-4.yaml
grep -q '^kind: Deployment' $f || exit 1
[ "$(grep -c '^kind:' $f)" = "1" ] || exit 1
grep -qE '^  replicas: 4$' $f || exit 1
[ -z "$(helm list -A -q)" ] || exit 1
