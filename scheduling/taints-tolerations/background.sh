#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
kubectl run drifter --image=nginx:1.27 --overrides='{"spec":{"nodeName":"node01"}}' >/dev/null
kubectl wait --for=condition=Ready pod/drifter --timeout=300s >/dev/null
touch /tmp/finished
