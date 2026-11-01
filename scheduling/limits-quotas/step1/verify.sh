#!/bin/bash
r=$(kubectl -n shipyard run lr-check --image=nginx:1.27 --dry-run=server -o jsonpath='{.spec.containers[0].resources.requests.cpu} {.spec.containers[0].resources.requests.memory} {.spec.containers[0].resources.limits.cpu} {.spec.containers[0].resources.limits.memory}')
[ "$r" = "100m 128Mi 500m 256Mi" ] || exit 1
kubectl -n shipyard get limitrange defaults >/dev/null 2>&1 || exit 1
