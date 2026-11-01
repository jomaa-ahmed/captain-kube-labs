#!/bin/bash
kubectl get node node01 -o jsonpath='{range .spec.taints[*]}{.key}={.value}:{.effect}{"\n"}{end}' | grep -qx 'team=gold:NoSchedule' || exit 1
[ "$(kubectl get node node01 -o jsonpath='{.metadata.labels.team}')" = "gold" ] || exit 1
