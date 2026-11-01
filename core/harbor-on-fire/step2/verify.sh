#!/bin/bash
[ "$(kubectl get svc -A --no-headers | grep -c harbor-web)" = "1" ] || exit 1
url=$(kubectl -n town get deploy visitor -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="TARGET")].value}')
echo "$url" | grep -q 'harbor-web\.harbor' || exit 1
kubectl -n town rollout status deploy/visitor --timeout=5s >/dev/null 2>&1 || exit 1
kubectl -n town logs deploy/visitor --tail=2 2>/dev/null | grep -q 'OK harbor reached' || exit 1
