#!/bin/bash
kubectl get node node01 -o jsonpath='{range .spec.taints[*]}{.key}={.value}:{.effect}{"\n"}{end}' | grep -qx 'storm=true:NoExecute' || exit 1
kubectl get pod drifter >/dev/null 2>&1 && exit 1
exit 0
