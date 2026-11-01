#!/bin/bash
[ "$(tr -d '[:space:]' < /root/hungry-reason.txt 2>/dev/null)" = "OOMKilled" ] || exit 1
[ "$(kubectl get pod hungry -o jsonpath='{.spec.containers[0].resources.limits.memory}')" = "256Mi" ] || exit 1
kubectl get pod hungry -o jsonpath='{.spec.containers[0].args}' | grep -q '150M' || exit 1
[ "$(kubectl get pod hungry -o jsonpath='{.status.containerStatuses[0].restartCount}')" = "0" ] || exit 1
kubectl get pod hungry -o jsonpath='{.status.containerStatuses[0].state.running.startedAt}' | grep -q . || exit 1
