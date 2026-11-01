#!/bin/bash
[ "$(kubectl get pod watchtower-node01 -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
kubectl get pod watchtower-node01 -o jsonpath='{.metadata.annotations}' | grep -q 'kubernetes.io/config.mirror' || exit 1
