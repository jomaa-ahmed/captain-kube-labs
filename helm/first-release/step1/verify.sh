#!/bin/bash
helm list -n docks --deployed -q | grep -qx web || exit 1
d=$(kubectl get deploy -n docks -l app.kubernetes.io/instance=web -o jsonpath='{.items[0].metadata.name}')
[ -n "$d" ] || exit 1
kubectl -n docks rollout status deploy/$d --timeout=5s >/dev/null 2>&1 || exit 1
