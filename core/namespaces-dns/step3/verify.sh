#!/bin/bash
[ "$(kubectl get svc -A -l app=shop --no-headers | wc -l)" = "1" ] || exit 1
kubectl -n market get svc shop >/dev/null 2>&1 || exit 1
kubectl -n docks rollout status deploy/buyer --timeout=5s >/dev/null 2>&1 || exit 1
kubectl -n docks logs deploy/buyer --tail=2 2>/dev/null | grep -q 'OK reached shop' || exit 1
