#!/bin/bash
f=/root/lighthouse.yaml
for k in apiVersion kind metadata spec; do grep -q "^$k:" $f || exit 1; done
[ "$(kubectl get pod lighthouse -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
[ "$(kubectl get pod lighthouse -o jsonpath='{.metadata.labels.app}')" = "harbor" ] || exit 1
[ "$(kubectl get pod lighthouse -o jsonpath='{.metadata.labels.tier}')" = "front" ] || exit 1
[ "$(kubectl get pod lighthouse -o jsonpath='{.spec.containers[0].image}')" = "nginx:1.27" ] || exit 1
