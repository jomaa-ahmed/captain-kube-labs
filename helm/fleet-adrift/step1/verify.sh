#!/bin/bash
[ "$(tr -d '[:space:]' < /root/secret-type.txt 2>/dev/null)" = "helm.sh/release.v1" ] || exit 1
helm list -n armada -a -q | grep -qx ghost && exit 1
kubectl get secret -n armada -l owner=helm,name=ghost --no-headers 2>/dev/null | grep -q . && exit 1
kubectl get deploy -n armada -l app.kubernetes.io/instance=ghost --no-headers 2>/dev/null | grep -q . && exit 1
exit 0
