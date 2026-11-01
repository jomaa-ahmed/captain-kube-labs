#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
kubectl taint nodes controlplane node-role.kubernetes.io/control-plane:NoSchedule- >/dev/null 2>&1 || true
touch /tmp/finished
