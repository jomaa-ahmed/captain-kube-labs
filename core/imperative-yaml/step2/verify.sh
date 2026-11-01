#!/bin/bash
grep -qE '^      terminationGracePeriodSeconds: 15$' /root/beacon.yaml || exit 1
kubectl apply -f /root/beacon.yaml --dry-run=server >/dev/null 2>&1 || exit 1
