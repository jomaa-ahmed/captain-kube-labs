#!/bin/bash
f=/root/beacon.yaml
grep -q '^kind: Deployment' $f || exit 1
grep -qE '^  name: beacon$' $f || exit 1
grep -qE '^  replicas: 2$' $f || exit 1
grep -q 'image: nginx:1.27' $f || exit 1
kubectl get deploy beacon >/dev/null 2>&1 && exit 1
exit 0
