#!/bin/bash
p=$(tr -d '[:space:]' < /root/new-pod.txt 2>/dev/null)
[ -n "$p" ] || exit 1
[ "$(kubectl get pod "$p" -o jsonpath='{.metadata.labels.app}' 2>/dev/null)" = "crew" ] || exit 1
rs=$(date -d "$(kubectl get rs crew -o jsonpath='{.metadata.creationTimestamp}')" +%s)
pod=$(date -d "$(kubectl get pod "$p" -o jsonpath='{.metadata.creationTimestamp}')" +%s)
[ $((pod - rs)) -ge 15 ] || exit 1
